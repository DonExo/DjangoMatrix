from matrix.forms import PackageRequestForm


class TestPackageRequestForm:
    def test_valid_github_url(self):
        form = PackageRequestForm(data={
            'name': 'Test',
            'repository_url': 'https://github.com/user/repo',
            'description': 'Test desc',
            'latest_version': '1.0'
        })
        assert form.is_valid()

    def test_invalid_github_url(self):
        form = PackageRequestForm(data={
            'name': 'Test',
            'repository_url': 'https://gitlab.com/user/repo',
            'description': 'Test desc',
            'latest_version': '1.0'
        })
        assert not form.is_valid()
        assert 'github.com' in form.errors['repository_url'][0]

    def test_invalid_url_structure(self):
        form = PackageRequestForm(data={
            'name': 'Test',
            'repository_url': 'https://github.com/invalid',
            'description': 'Test desc',
            'latest_version': '1.0'
        })
        assert not form.is_valid()
        assert 'two components' in form.errors['repository_url'][0]
