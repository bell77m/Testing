#test
def test_example(page):
    page.goto('https://example.com')

    assert page.title() == 'Example Domain'
