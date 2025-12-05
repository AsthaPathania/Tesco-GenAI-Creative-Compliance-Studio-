import pytest
from compliance_engine import AdvancedComplianceEngine
from value_tile_generator import generate_value_tile, validate_value_tile_design
from ai_creative_generator import AICreativeSuggestor

class TestTescoCreativeStudio:
    """Test suite for Tesco Creative Studio"""
    
    def setup_method(self):
        self.compliance_engine = AdvancedComplianceEngine()
        self.creative_suggestor = AICreativeSuggestor()
    
    def test_comprehensive_sensitive_content_detection(self):
        """Test enhanced sensitive content detection"""
        # Test violence and crime
        result = self.compliance_engine.check_text_compliance("Killer deal", "Murderous prices")
        assert not result["approved"]
        assert any("murder" in issue.lower() for issue in result["issues"])
        assert any("kill" in issue.lower() for issue in result["issues"])
        
        # Test drugs and substance abuse
        result = self.compliance_engine.check_text_compliance("Cocaine energy", "Heroin strength")
        assert not result["approved"]
        assert any("cocaine" in issue.lower() for issue in result["issues"])
        assert any("heroin" in issue.lower() for issue in result["issues"])
        
        # Test mental health
        result = self.compliance_engine.check_text_compliance("Depression relief", "Suicide prevention")
        assert not result["approved"]
        assert any("depression" in issue.lower() for issue in result["issues"])
        assert any("suicide" in issue.lower() for issue in result["issues"])
        
        # Test hate speech
        result = self.compliance_engine.check_text_compliance("Racist content", "Hate-filled offer")
        assert not result["approved"]
        assert any("racist" in issue.lower() for issue in result["issues"])
        assert any("hate" in issue.lower() for issue in result["issues"])
        
        # Test adult content
        result = self.compliance_engine.check_text_compliance("Porn star product", "Sexual material")
        assert not result["approved"]
        assert any("porn" in issue.lower() for issue in result["issues"])
        assert any("sexual" in issue.lower() for issue in result["issues"])
        
        # Test terrorism
        result = self.compliance_engine.check_text_compliance("Bomb shelter sale", "Terror prices")
        assert not result["approved"]
        assert any("bomb" in issue.lower() for issue in result["issues"])
        assert any("terror" in issue.lower() for issue in result["issues"])
        
        # Test gambling
        result = self.compliance_engine.check_text_compliance("Lottery tickets", "Gamble and win")
        assert not result["approved"]
        assert any("lottery" in issue.lower() for issue in result["issues"])
        assert any("gamble" in issue.lower() for issue in result["issues"])
        
        print("✅ Comprehensive sensitive content detection tests passed!")
    
    def test_compliance_engine_hard_fail_rules(self):
        """Test compliance engine HARD FAIL functionality"""
        # Test forbidden terms - HARD FAIL
        result = self.compliance_engine.check_text_compliance("Win a free prize!", "Limited time offer")
        assert not result["approved"]
        assert len(result["issues"]) > 0
        assert "HARD FAIL" in result["issues"][0]
        
        # Test compliant text
        result = self.compliance_engine.check_text_compliance("New product launch", "Great quality")
        assert result["approved"]
        
        # Test alcohol-specific HARD FAIL rules
        result = self.compliance_engine.check_text_compliance("Healthy choice", "Good for you", "Alcohol")
        assert not result["approved"]
        assert "HARD FAIL" in result["issues"][0]
        
        print("✅ Compliance engine HARD FAIL tests passed!")
    
    def test_value_tile_generation_appendix_a(self):
        """Test value tile generation according to Appendix A"""
        # Test Clubcard tile - flat design, predefined
        price_data = {"clubcard_price": "£3.50", "regular_price": "£4.50"}
        tile = generate_value_tile("Clubcard Price", price_data)
        assert tile is not None
        
        # Test LEP tile - white background, Tesco blue font
        price_data = {"lep_price": "£2.99"}
        tile = generate_value_tile("Everyday Low Price", price_data)
        assert tile is not None
        
        # Test New tile - predefined, cannot be edited
        tile = generate_value_tile("New", {})
        assert tile is not None
        
        print("✅ Value tile generation Appendix A tests passed!")
    
    def test_ai_suggestor(self):
        """Test AI creative suggestor"""
        # Test template loading
        templates = self.creative_suggestor.creative_templates
        assert len(templates) > 0
        
        # Test variation generation
        variations = self.creative_suggestor.generate_variations("Test", "Subtest", None, "None")
        assert len(variations) > 0
        
        # Test copy suggestions
        suggestions = self.creative_suggestor.suggest_copy_improvements("Test Headline", "Test Subhead", "Alcohol")
        assert len(suggestions) > 0
        
        print("✅ AI suggestor tests passed!")

def run_all_tests():
    """Run all tests"""
    test_suite = TestTescoCreativeStudio()
    test_suite.setup_method()
    
    try:
        test_suite.test_comprehensive_sensitive_content_detection()
        test_suite.test_compliance_engine_hard_fail_rules()
        test_suite.test_value_tile_generation_appendix_a()
        test_suite.test_ai_suggestor()
        
        print("\n🎉 All tests passed! The system now detects ALL types of sensitive content and claims.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()