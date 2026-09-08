"""Generic regressions for citation failures; no real source text or profiles."""
import unittest
from contracts import Invalid, SCHEMAS, response_schema, validate


class SourceContractTests(unittest.TestCase):
    def schema(self):
        return response_schema('intake', ['product', 'history', 'persona'], ['product'])

    def test_product_references_cannot_use_historical_source(self):
        refs = self.schema()['properties']['product_refs']
        with self.assertRaisesRegex(Invalid, 'invalid enum'):
            validate([dict(source_id='history', quote='Generic example')], refs)

    def test_history_and_persona_refs_retain_their_own_source_options(self):
        props = self.schema()['properties']
        for section in ['historical_names', 'priority_personas']:
            refs = props[section]['items']['properties']['source_refs']
            validate([dict(source_id='history', quote='Generic example')], refs)
        self.assertNotIn('enum', SCHEMAS['intake']['properties']['product_refs']['items']['properties']['source_id'])

    def test_empty_historical_citation_is_rejected_at_schema_boundary(self):
        refs = self.schema()['properties']['historical_names']['items']['properties']['source_refs']
        with self.assertRaisesRegex(Invalid, 'at least 1'):
            validate([], refs, '$.historical_names[0].source_refs')

    def test_persona_schema_only_allows_own_profile(self):
        schema = response_schema('persona', ['p1', 'p2'], ['product'], 'p1')
        refs = schema['properties']['reviews']['items']['properties']['source_refs']
        validate([dict(source_id='p1', quote='Example')], refs)
        with self.assertRaisesRegex(Invalid, 'invalid enum'):
            validate([dict(source_id='p2', quote='Example')], refs)


if __name__ == '__main__':
    unittest.main()
