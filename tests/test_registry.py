from domains.registry import list_domains


def test_all_domains_available():
    domains = list_domains()
    assert len(domains) == 32
    assert all(len(domain.columns) >= 20 for domain in domains)
