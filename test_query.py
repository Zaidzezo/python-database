import unittest

from exceptions import (
    AtlasDBError,
    QueryError,
    InvalidQueryError,
    UnsupportedOperatorError,
)
from query import validate_query, match_query, apply_operator


class TestMatchQueryEquality(unittest.TestCase):
    """Test plain equality matching, including nested documents and None."""

    def test_simple_equality_match(self):
        document = {"name": "Zaid", "age": 25}
        self.assertTrue(match_query(document, {"name": "Zaid"}))

    def test_simple_equality_non_match(self):
        document = {"name": "Zaid", "age": 25}
        self.assertFalse(match_query(document, {"name": "Sara"}))

    def test_missing_field_is_non_match(self):
        document = {"name": "Zaid"}
        self.assertFalse(match_query(document, {"city": "Amman"}))

    def test_empty_query_matches_everything(self):
        document = {"name": "Zaid"}
        self.assertTrue(match_query(document, {}))

    def test_none_matches_explicit_null_field(self):
        document = {"name": "Zaid", "middle_name": None}
        self.assertTrue(match_query(document, {"middle_name": None}))

    def test_none_does_not_match_missing_field(self):
        document = {"name": "Zaid"}
        self.assertFalse(match_query(document, {"middle_name": None}))

    def test_boolean_distinct_from_number_in_equality(self):
        document = {"active": True}
        self.assertFalse(match_query(document, {"active": 1}))
        self.assertTrue(match_query(document, {"active": True}))

    def test_nested_document_exact_match(self):
        document = {"user": {"years": 30, "months": 6}}
        query = {"user": {"years": 30, "months": 6}}
        self.assertTrue(match_query(document, query))

    def test_nested_document_partial_match(self):
        # Per the project's own design decision: nested fields use the
        # same partial-match semantics as top-level fields.
        document = {"user": {"years": 30, "months": 6, "city": "Amman"}}
        query = {"user": {"years": 30}}
        self.assertTrue(match_query(document, query))

    def test_nested_document_non_match(self):
        document = {"user": {"years": 30}}
        query = {"user": {"years": 99}}
        self.assertFalse(match_query(document, query))

    def test_implicit_and_all_fields_match(self):
        document = {"name": "Zaid", "age": 25}
        query = {"name": "Zaid", "age": 25}
        self.assertTrue(match_query(document, query))

    def test_implicit_and_one_field_fails(self):
        document = {"name": "Zaid", "age": 25}
        query = {"name": "Zaid", "age": 99}
        self.assertFalse(match_query(document, query))


class TestMatchQueryOperators(unittest.TestCase):
    """Test $gt, $lt, $gte, $lte and combined operator conditions."""

    def test_gt_match(self):
        self.assertTrue(match_query({"age": 25}, {"age": {"$gt": 20}}))

    def test_gt_non_match(self):
        self.assertFalse(match_query({"age": 15}, {"age": {"$gt": 20}}))

    def test_lt_match(self):
        self.assertTrue(match_query({"age": 15}, {"age": {"$lt": 20}}))

    def test_lt_non_match(self):
        self.assertFalse(match_query({"age": 25}, {"age": {"$lt": 20}}))

    def test_gte_boundary_matches(self):
        self.assertTrue(match_query({"age": 20}, {"age": {"$gte": 20}}))

    def test_gte_below_boundary_non_match(self):
        self.assertFalse(match_query({"age": 19}, {"age": {"$gte": 20}}))

    def test_lte_boundary_matches(self):
        self.assertTrue(match_query({"age": 20}, {"age": {"$lte": 20}}))

    def test_lte_above_boundary_non_match(self):
        self.assertFalse(match_query({"age": 21}, {"age": {"$lte": 20}}))

    def test_combined_operators_and_semantics_both_pass(self):
        query = {"age": {"$gte": 18, "$lt": 30}}
        self.assertTrue(match_query({"age": 25}, query))

    def test_combined_operators_and_semantics_one_fails(self):
        query = {"age": {"$gte": 18, "$lt": 30}}
        self.assertFalse(match_query({"age": 35}, query))

    def test_operator_on_missing_field_is_non_match(self):
        self.assertFalse(match_query({"name": "Zaid"}, {"age": {"$gt": 20}}))

    def test_operator_on_incompatible_stored_type_is_non_match(self):
        # stored value is a string, operand is a number -> non-match, not an error
        self.assertFalse(match_query({"age": "hello"}, {"age": {"$gt": 20}}))

    def test_operator_numeric_cross_type_int_and_float(self):
        self.assertTrue(match_query({"price": 20.5}, {"price": {"$gt": 20}}))

    def test_operator_string_comparison(self):
        self.assertTrue(match_query({"name": "Zara"}, {"name": {"$gt": "Zaid"}}))

    def test_operator_boolean_stored_value_is_non_match(self):
        # Booleans are distinct from numbers, so comparing against a
        # boolean-stored field should never match, never error.
        self.assertFalse(match_query({"active": True}, {"active": {"$gt": 0}}))


class TestMatchQueryOr(unittest.TestCase):
    """Test $or, including combination with AND and nested $or."""

    def test_or_first_branch_matches(self):
        query = {"$or": [{"name": "Zaid"}, {"name": "Sara"}]}
        self.assertTrue(match_query({"name": "Zaid"}, query))

    def test_or_second_branch_matches(self):
        query = {"$or": [{"name": "Zaid"}, {"name": "Sara"}]}
        self.assertTrue(match_query({"name": "Sara"}, query))

    def test_or_no_branch_matches(self):
        query = {"$or": [{"name": "Zaid"}, {"name": "Sara"}]}
        self.assertFalse(match_query({"name": "Omar"}, query))

    def test_or_combined_with_and(self):
        document = {"name": "Zaid", "age": 25}
        query = {"age": 25, "$or": [{"name": "Zaid"}, {"name": "Sara"}]}
        self.assertTrue(match_query(document, query))

    def test_or_combined_with_and_fails_on_and_part(self):
        document = {"name": "Zaid", "age": 99}
        query = {"age": 25, "$or": [{"name": "Zaid"}, {"name": "Sara"}]}
        self.assertFalse(match_query(document, query))

    def test_nested_or(self):
        document = {"name": "Sara", "age": 17}
        query = {
            "$or": [
                {"name": "Zaid"},
                {"$or": [{"age": 17}, {"age": 18}]},
            ]
        }
        self.assertTrue(match_query(document, query))

    def test_nested_query_against_string_field_is_non_match_not_error(self):
        document = {"name": "Ali"}
        query = {"name": {"foo": "bar"}}
        self.assertFalse(match_query(document, query))

    def test_nested_query_against_numeric_field_is_non_match_not_error(self):
        document = {"age": 25}
        query = {"age": {"foo": "bar"}}
        self.assertFalse(match_query(document, query))

    def test_nested_query_against_list_field_is_non_match_not_error(self):
        document = {"tags": [1, 2, 3]}
        query = {"tags": {"foo": "bar"}}
        self.assertFalse(match_query(document, query))

    def test_nested_query_against_none_field_is_non_match_not_error(self):
        document = {"metadata": None}
        query = {"metadata": {"foo": "bar"}}
        self.assertFalse(match_query(document, query))

    def test_nested_query_against_boolean_field_is_non_match_not_error(self):
        document = {"active": True}
        query = {"active": {"foo": "bar"}}
        self.assertFalse(match_query(document, query))


class TestValidateQuery(unittest.TestCase):
    """Test upfront validation: types, structure, operators, operands."""

    def test_non_dict_query_raises_typeerror(self):
        with self.assertRaises(TypeError):
            validate_query("not a dict")

    def test_valid_simple_query_raises_nothing(self):
        validate_query({"name": "Zaid"})  # should not raise

    def test_valid_operator_query_raises_nothing(self):
        validate_query({"age": {"$gt": 20}})  # should not raise

    def test_unsupported_operator_raises_unsupportedoperatorerror(self):
        with self.assertRaises(UnsupportedOperatorError):
            validate_query({"age": {"$invalid_op": 20}})

    def test_invalid_operand_type_raises_invalidqueryerror(self):
        with self.assertRaises(InvalidQueryError):
            validate_query({"age": {"$gt": [1, 2, 3]}})

    def test_boolean_operand_raises_invalidqueryerror(self):
        with self.assertRaises(InvalidQueryError):
            validate_query({"age": {"$gt": True}})

    def test_or_with_non_list_value_raises_invalidqueryerror(self):
        with self.assertRaises(InvalidQueryError):
            validate_query({"$or": "not a list"})

    def test_or_branch_is_validated_recursively(self):
        with self.assertRaises(UnsupportedOperatorError):
            validate_query({"$or": [{"age": {"$bad_op": 1}}]})

    def test_nested_document_is_validated_recursively(self):
        with self.assertRaises(UnsupportedOperatorError):
            validate_query({"user": {"age": {"$bad_op": 1}}})

    def test_unsupported_operator_is_subclass_of_invalidqueryerror(self):
        # Confirms the exception hierarchy from the design doc.
        self.assertTrue(issubclass(UnsupportedOperatorError, InvalidQueryError))
        self.assertTrue(issubclass(InvalidQueryError, QueryError))
        self.assertTrue(issubclass(QueryError, AtlasDBError))

    def test_validation_runs_on_malformed_query_with_no_documents(self):
        # The point of upfront validation: it must raise even though
        # there is nothing to scan. match_query is never reached.
        with self.assertRaises(UnsupportedOperatorError):
            validate_query({"age": {"$nope": 1}})

    def test_top_level_and_raises_unsupportedoperatorerror(self):
        with self.assertRaises(UnsupportedOperatorError):
            validate_query({"$and": [{"name": "Zaid"}, {"name": "Sara"}]})

    def test_or_subquery_containing_and_raises_unsupportedoperatorerror(self):
        # $and nested inside a validated $or branch must also be caught,
        # not just at the top level.
        with self.assertRaises(UnsupportedOperatorError):
            validate_query({"$or": [{"$and": [{"name": "Zaid"}]}]})

    def test_arbitrary_unknown_dollar_key_raises_unsupportedoperatorerror(self):
        # Not just $and specifically -- any unrecognized top-level $-key.
        with self.assertRaises(UnsupportedOperatorError):
            validate_query({"$nonexistent": "whatever"})


class TestApplyOperator(unittest.TestCase):
    """Test apply_operator directly: stored-value compatibility only."""

    def test_incompatible_stored_type_is_non_match(self):
        self.assertFalse(apply_operator("$gt", 20, "hello"))

    def test_string_vs_string_comparison(self):
        self.assertTrue(apply_operator("$gt", "Zaid", "Zara"))

    def test_number_vs_number_comparison_int_and_float(self):
        self.assertTrue(apply_operator("$gte", 20, 20.0))

    def test_boolean_stored_value_is_non_match(self):
        self.assertFalse(apply_operator("$gt", 0, True))


if __name__ == "__main__":
    unittest.main()