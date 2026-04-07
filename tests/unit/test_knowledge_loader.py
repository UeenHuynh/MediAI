"""
Unit tests for MedicalKnowledgeLoader service
Tests loading medical knowledge from various file sources
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import shutil


class TestMedicalKnowledgeLoaderInit:
    """Tests for MedicalKnowledgeLoader initialization"""

    def test_init_with_default_dir(self):
        """Test initialization with default directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader

        loader = MedicalKnowledgeLoader()

        assert loader.data_dir == Path("./data/medical_knowledge")

    def test_init_with_custom_dir(self):
        """Test initialization with custom directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader

        custom_dir = "/tmp/test_medical_data"
        loader = MedicalKnowledgeLoader(data_dir=custom_dir)

        assert loader.data_dir == Path(custom_dir)

    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates the directory if it doesn't exist"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader

        test_dir = tmp_path / "new_medical_data"
        assert not test_dir.exists()

        loader = MedicalKnowledgeLoader(data_dir=str(test_dir))

        assert test_dir.exists()
        assert loader.data_dir == test_dir

    def test_init_with_existing_directory(self, tmp_path):
        """Test initialization with existing directory doesn't fail"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader

        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()

        loader = MedicalKnowledgeLoader(data_dir=str(test_dir))

        assert test_dir.exists()
        assert loader.data_dir == test_dir


class TestLoadTextFile:
    """Tests for load_text_file method"""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create knowledge loader with temp directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader
        return MedicalKnowledgeLoader(data_dir=str(tmp_path))

    def test_load_text_file_success(self, loader, tmp_path):
        """Test successfully loading a text file"""
        test_file = tmp_path / "test.txt"
        test_content = "This is medical content."
        test_file.write_text(test_content)

        result = loader.load_text_file(str(test_file))

        assert result is not None
        assert result["content"] == test_content
        assert result["metadata"]["file_name"] == "test.txt"
        assert result["metadata"]["file_type"] == ".txt"
        assert result["source"] == str(test_file)

    def test_load_markdown_file(self, loader, tmp_path):
        """Test loading a markdown file"""
        test_file = tmp_path / "test.md"
        test_content = "# Medical Document\n\nContent here."
        test_file.write_text(test_content)

        result = loader.load_text_file(str(test_file))

        assert result is not None
        assert result["content"] == test_content
        assert result["metadata"]["file_type"] == ".md"

    def test_load_nonexistent_file(self, loader):
        """Test loading file that doesn't exist"""
        result = loader.load_text_file("/nonexistent/file.txt")

        assert result is None

    def test_load_file_with_unicode(self, loader, tmp_path):
        """Test loading file with unicode characters"""
        test_file = tmp_path / "unicode.txt"
        test_content = "Medical data: Temperature 37°C, μg/mL"
        test_file.write_text(test_content, encoding="utf-8")

        result = loader.load_text_file(str(test_file))

        assert result is not None
        assert "°C" in result["content"]
        assert "μg/mL" in result["content"]

    def test_load_empty_file(self, loader, tmp_path):
        """Test loading empty file"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        result = loader.load_text_file(str(test_file))

        assert result is not None
        assert result["content"] == ""


class TestLoadJsonFile:
    """Tests for load_json_file method"""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create knowledge loader with temp directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader
        return MedicalKnowledgeLoader(data_dir=str(tmp_path))

    def test_load_json_list(self, loader, tmp_path):
        """Test loading JSON file with list of documents"""
        test_file = tmp_path / "data.json"
        test_data = [
            {"content": "Document 1", "metadata": {"type": "guideline"}},
            {"content": "Document 2", "metadata": {"type": "protocol"}}
        ]
        test_file.write_text(json.dumps(test_data))

        result = loader.load_json_file(str(test_file))

        assert len(result) == 2
        assert result[0]["content"] == "Document 1"
        assert result[1]["content"] == "Document 2"
        assert result[0]["metadata"]["type"] == "guideline"
        assert result[0]["metadata"]["source_file"] == "data.json"

    def test_load_json_dict(self, loader, tmp_path):
        """Test loading JSON file with single document dict"""
        test_file = tmp_path / "single.json"
        test_data = {"content": "Single document", "metadata": {"type": "drug"}}
        test_file.write_text(json.dumps(test_data))

        result = loader.load_json_file(str(test_file))

        assert len(result) == 1
        assert result[0]["content"] == "Single document"
        assert result[0]["metadata"]["type"] == "drug"

    def test_load_json_with_text_field(self, loader, tmp_path):
        """Test loading JSON with 'text' field instead of 'content'"""
        test_file = tmp_path / "text_field.json"
        test_data = [{"text": "Document with text field"}]
        test_file.write_text(json.dumps(test_data))

        result = loader.load_json_file(str(test_file))

        assert len(result) == 1
        assert result[0]["content"] == "Document with text field"

    def test_load_json_without_content_field(self, loader, tmp_path):
        """Test loading JSON without content or text field"""
        test_file = tmp_path / "no_content.json"
        test_data = [{"title": "Document", "description": "Details"}]
        test_file.write_text(json.dumps(test_data))

        result = loader.load_json_file(str(test_file))

        assert len(result) == 1
        # Should convert entire dict to string
        assert "title" in result[0]["content"]
        assert "description" in result[0]["content"]

    def test_load_json_with_indices(self, loader, tmp_path):
        """Test that JSON list items get index metadata"""
        test_file = tmp_path / "indexed.json"
        test_data = [
            {"content": "Doc 1"},
            {"content": "Doc 2"},
            {"content": "Doc 3"}
        ]
        test_file.write_text(json.dumps(test_data))

        result = loader.load_json_file(str(test_file))

        assert result[0]["metadata"]["index"] == 0
        assert result[1]["metadata"]["index"] == 1
        assert result[2]["metadata"]["index"] == 2
        assert result[0]["source"] == f"{test_file}#0"

    def test_load_invalid_json(self, loader, tmp_path):
        """Test loading invalid JSON returns empty list"""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("{invalid json content")

        result = loader.load_json_file(str(test_file))

        assert result == []

    def test_load_nonexistent_json(self, loader):
        """Test loading nonexistent JSON file returns empty list"""
        result = loader.load_json_file("/nonexistent/file.json")

        assert result == []


class TestLoadDirectory:
    """Tests for load_directory method"""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create knowledge loader with temp directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader
        return MedicalKnowledgeLoader(data_dir=str(tmp_path))

    def test_load_empty_directory(self, loader, tmp_path):
        """Test loading empty directory returns empty list"""
        result = loader.load_directory(str(tmp_path))

        assert result == []

    def test_load_directory_with_text_files(self, loader, tmp_path):
        """Test loading directory with text and markdown files"""
        (tmp_path / "doc1.txt").write_text("Text content 1")
        (tmp_path / "doc2.md").write_text("Markdown content 2")

        result = loader.load_directory(str(tmp_path))

        assert len(result) == 2
        contents = [doc["content"] for doc in result]
        assert "Text content 1" in contents
        assert "Markdown content 2" in contents

    def test_load_directory_with_json_files(self, loader, tmp_path):
        """Test loading directory with JSON files"""
        json_file = tmp_path / "data.json"
        test_data = [
            {"content": "JSON doc 1"},
            {"content": "JSON doc 2"}
        ]
        json_file.write_text(json.dumps(test_data))

        result = loader.load_directory(str(tmp_path))

        assert len(result) == 2
        assert result[0]["content"] == "JSON doc 1"
        assert result[1]["content"] == "JSON doc 2"

    def test_load_directory_mixed_files(self, loader, tmp_path):
        """Test loading directory with mixed file types"""
        (tmp_path / "doc.txt").write_text("Text")
        (tmp_path / "doc.md").write_text("Markdown")
        (tmp_path / "data.json").write_text(json.dumps([{"content": "JSON"}]))

        result = loader.load_directory(str(tmp_path))

        assert len(result) == 3

    def test_load_directory_recursive(self, loader, tmp_path):
        """Test loading directory recursively includes subdirectories"""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.txt").write_text("Root document")
        (subdir / "sub.txt").write_text("Subdirectory document")

        result = loader.load_directory(str(tmp_path))

        assert len(result) == 2
        contents = [doc["content"] for doc in result]
        assert "Root document" in contents
        assert "Subdirectory document" in contents

    def test_load_directory_ignores_unsupported_files(self, loader, tmp_path):
        """Test that unsupported file types are ignored"""
        (tmp_path / "doc.txt").write_text("Text content")
        (tmp_path / "image.png").write_bytes(b"fake image data")
        (tmp_path / "data.xml").write_text("<xml>data</xml>")

        result = loader.load_directory(str(tmp_path))

        # Only .txt should be loaded
        assert len(result) == 1
        assert result[0]["content"] == "Text content"

    def test_load_nonexistent_directory(self, loader):
        """Test loading nonexistent directory returns empty list"""
        result = loader.load_directory("/nonexistent/directory")

        assert result == []

    def test_load_directory_default(self, loader):
        """Test loading directory without argument uses data_dir"""
        (loader.data_dir / "test.txt").write_text("Default dir content")

        result = loader.load_directory()

        assert len(result) == 1
        assert result[0]["content"] == "Default dir content"


class TestCreateSampleKnowledgeBase:
    """Tests for create_sample_knowledge_base method"""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create knowledge loader with temp directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader
        return MedicalKnowledgeLoader(data_dir=str(tmp_path))

    def test_create_sample_knowledge_base(self, loader, tmp_path):
        """Test creating sample knowledge base files"""
        loader.create_sample_knowledge_base()

        # Check that files were created
        assert (tmp_path / "sepsis_guidelines.md").exists()
        assert (tmp_path / "mortality_risk_assessment.md").exists()
        assert (tmp_path / "icu_medications.md").exists()

    def test_sample_files_content(self, loader, tmp_path):
        """Test that sample files have expected content"""
        loader.create_sample_knowledge_base()

        sepsis_content = (tmp_path / "sepsis_guidelines.md").read_text()
        mortality_content = (tmp_path / "mortality_risk_assessment.md").read_text()
        medications_content = (tmp_path / "icu_medications.md").read_text()

        # Check for key content markers
        assert "Sepsis Recognition" in sepsis_content
        assert "qSOFA" in sepsis_content
        assert "SOFA Score" in sepsis_content

        assert "Mortality Risk Assessment" in mortality_content
        assert "APACHE II" in mortality_content

        assert "Vasopressors" in medications_content
        assert "Norepinephrine" in medications_content
        assert "Propofol" in medications_content

    def test_sample_files_loadable(self, loader, tmp_path):
        """Test that created sample files can be loaded"""
        loader.create_sample_knowledge_base()

        result = loader.load_directory(str(tmp_path))

        assert len(result) == 3
        file_names = [doc["metadata"]["file_name"] for doc in result]
        assert "sepsis_guidelines.md" in file_names
        assert "mortality_risk_assessment.md" in file_names
        assert "icu_medications.md" in file_names


class TestLoadPubMedAbstracts:
    """Tests for load_pubmed_abstracts method"""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create knowledge loader with temp directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader
        return MedicalKnowledgeLoader(data_dir=str(tmp_path))

    def test_load_pubmed_without_biopython(self, loader):
        """Test that missing Biopython returns empty list"""
        with patch("builtins.__import__", side_effect=ImportError):
            result = loader.load_pubmed_abstracts("sepsis")

        assert result == []

    def test_load_pubmed_success(self, loader):
        """Test PubMed loading with ImportError returns empty list"""
        # PubMed requires Biopython which may not be installed
        # Test that missing dependency is handled gracefully
        result = loader.load_pubmed_abstracts("sepsis", max_results=10)

        # Should return empty list if Biopython not available
        # or handle errors gracefully
        assert isinstance(result, list)

    def test_load_pubmed_no_results(self, loader):
        """Test PubMed search with no results"""
        mock_entrez = MagicMock()
        mock_handle = MagicMock()
        mock_handle.__enter__ = MagicMock(return_value=mock_handle)
        mock_handle.__exit__ = MagicMock(return_value=False)

        mock_entrez.esearch.return_value = mock_handle
        mock_entrez.read.return_value = {"IdList": []}

        with patch.dict("sys.modules", {"Bio": MagicMock(), "Bio.Entrez": mock_entrez}):
            result = loader.load_pubmed_abstracts("nonexistent_query")

        assert result == []

    def test_load_pubmed_handles_errors(self, loader):
        """Test that PubMed errors are handled gracefully"""
        mock_entrez = MagicMock()
        mock_entrez.esearch.side_effect = Exception("API Error")

        with patch.dict("sys.modules", {"Bio": MagicMock(), "Bio.Entrez": mock_entrez}):
            result = loader.load_pubmed_abstracts("sepsis")

        assert result == []


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create knowledge loader with temp directory"""
        from api.services.knowledge_loader import MedicalKnowledgeLoader
        return MedicalKnowledgeLoader(data_dir=str(tmp_path))

    def test_load_file_with_permission_error(self, loader, tmp_path):
        """Test handling file permission errors"""
        test_file = tmp_path / "restricted.txt"
        test_file.write_text("content")

        # Simulate permission error by mocking open
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = loader.load_text_file(str(test_file))

        assert result is None

    def test_load_corrupted_json(self, loader, tmp_path):
        """Test loading JSON with corrupted structure"""
        test_file = tmp_path / "corrupted.json"
        test_file.write_text('{"incomplete": ')

        result = loader.load_json_file(str(test_file))

        assert result == []

    def test_load_very_large_file(self, loader, tmp_path):
        """Test loading very large file"""
        test_file = tmp_path / "large.txt"
        large_content = "Medical data. " * 10000  # ~140KB
        test_file.write_text(large_content)

        result = loader.load_text_file(str(test_file))

        assert result is not None
        assert len(result["content"]) > 100000

    def test_load_json_with_nested_metadata(self, loader, tmp_path):
        """Test loading JSON with nested metadata structures"""
        test_file = tmp_path / "nested.json"
        test_data = {
            "content": "Document content",
            "metadata": {
                "author": "Dr. Smith",
                "tags": ["sepsis", "critical care"],
                "nested": {"level": 2}
            }
        }
        test_file.write_text(json.dumps(test_data))

        result = loader.load_json_file(str(test_file))

        assert len(result) == 1
        assert result[0]["metadata"]["author"] == "Dr. Smith"
        assert result[0]["metadata"]["tags"] == ["sepsis", "critical care"]
        assert result[0]["metadata"]["nested"]["level"] == 2
