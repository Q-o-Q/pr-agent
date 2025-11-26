import pytest
from unittest.mock import MagicMock, patch

from pr_agent.algo.types import EDIT_TYPE, FilePatchInfo
from pr_agent.git_providers.github_provider import GithubProvider


class TestPRProcessing:
    """测试PR处理的核心功能"""

    def test_parse_pr_url_valid(self):
        """测试解析有效的PR URL"""
        url = "https://github.com/owner/repo/pull/123"
        owner, repo, pr_number = GithubProvider._parse_pr_url(url)
        assert owner == "owner"
        assert repo == "repo"
        assert pr_number == 123

    def test_parse_pr_url_invalid(self):
        """测试解析无效的PR URL"""
        url = "https://github.com/owner/repo"
        with pytest.raises(ValueError):
            GithubProvider._parse_pr_url(url)

    @patch("pr_agent.git_providers.github_provider.requests.get")
    def test_fetch_pr_details_success(self, mock_get):
        """测试成功获取PR详情"""
        # Mock响应数据
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test PR",
            "body": "This is a test PR",
            "state": "open",
            "user": {"login": "testuser"},
        }
        mock_get.return_value = mock_response

        provider = GithubProvider(pr_url="https://github.com/owner/repo/pull/123")
        details = provider.get_pr_details()

        assert details["title"] == "Test PR"
        assert details["body"] == "This is a test PR"
        assert details["state"] == "open"

    def test_file_patch_info_creation(self):
        """测试FilePatchInfo对象的创建"""
        patch_info = FilePatchInfo(
            filename="test.py",
            patch_content="@@ -1,5 +1,5 @@\n-old line\n+new line",
            edit_type=EDIT_TYPE.MODIFIED,
        )

        assert patch_info.filename == "test.py"
        assert patch_info.edit_type == EDIT_TYPE.MODIFIED
        assert "old line" in patch_info.patch_content
        assert "new line" in patch_info.patch_content

    @patch("pr_agent.git_providers.github_provider.requests.post")
    def test_post_comment_success(self, mock_post):
        """测试成功发布评论"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        provider = GithubProvider(pr_url="https://github.com/owner/repo/pull/123")
        result = provider.publish_comment("Test comment")

        assert result is True
        mock_post.assert_called_once()

    def test_edit_type_enum_values(self):
        """测试EDIT_TYPE枚举值"""
        assert EDIT_TYPE.ADDED.value == "ADDED"
        assert EDIT_TYPE.MODIFIED.value == "MODIFIED"
        assert EDIT_TYPE.DELETED.value == "DELETED"
        assert EDIT_TYPE.RENAMED.value == "RENAMED"


class TestPRValidation:
    """测试PR验证功能"""

    def test_validate_pr_title_valid(self):
        """测试验证有效的PR标题"""
        title = "feat: add new feature"
        # 这里可以添加实际的验证逻辑测试
        assert len(title) > 0
        assert isinstance(title, str)

    def test_validate_pr_title_empty(self):
        """测试验证空的PR标题"""
        title = ""
        # 这里可以添加实际的验证逻辑测试
        assert len(title) == 0

    @pytest.mark.parametrize(
        "description,expected",
        [("Detailed description", True), ("", False), (None, False)],
    )
    def test_validate_pr_description(self, description, expected):
        """参数化测试PR描述验证"""
        # 这里可以添加实际的验证逻辑测试
        if description:
            result = len(description) > 0
        else:
            result = False
        assert result == expected
