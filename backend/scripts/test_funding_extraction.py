#!/usr/bin/env python3
"""
Enhanced Funding Extraction Testing Script
==========================================

This script tests the enhanced funding extractor to validate its ability to 
extract funding and market sizing information from various text patterns.
"""

import sys
from pathlib import Path
import json

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.examples.enhanced_funding_extractor import EnhancedFundingExtractor


def test_funding_extraction():
    """Test funding extraction with various patterns"""
    
    print("🧪 Testing Enhanced Funding Extraction")
    print("=" * 50)
    
    extractor = EnhancedFundingExtractor()
    
    # Test cases covering different funding patterns
    test_cases = [
        {
            "name": "Total Pool Pattern",
            "text": "The African Innovation Fund announces $5 million total funding to support 10-15 AI startups across the continent, focusing on healthcare and fintech solutions.",
            "expected_type": "total_pool"
        },
        {
            "name": "Exact Amount Pattern", 
            "text": "Each selected project will receive exactly $50,000 to develop AI solutions for healthcare challenges in Nigeria and Kenya.",
            "expected_type": "per_project_exact"
        },
        {
            "name": "Range Pattern",
            "text": "Grants ranging from $25,000 to $100,000 are available for women-led AI ventures focusing on fintech and edtech solutions across Africa.",
            "expected_type": "per_project_range"
        },
        {
            "name": "Market Sizing Pattern",
            "text": "The African fintech market is worth $12 billion and growing at 30% annually. The total addressable market (TAM) for AI-powered financial services is estimated at $3.2 billion.",
            "expected_market_data": True
        },
        {
            "name": "Complex Funding + Market",
            "text": "The $50 million Nigeria AI Development Fund will support 20-30 startups with grants of $1-2 million each. The Nigerian AI market represents a $800 million opportunity, with the healthcare AI sector alone worth $150 million.",
            "expected_type": "total_pool",
            "expected_market_data": True
        },
        {
            "name": "Publication Funding Pattern",
            "text": "This research was supported by grants from the Nigerian Research Foundation (NRF-2023-AI-001, $75,000) and the African AI Initiative ($25,000).",
            "expected_funding_mentions": True
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['name']}")
        print(f"Text: {test_case['text'][:100]}...")
        
        # Extract funding information
        funding_info = extractor.extract_funding_info(test_case['text'])
        
        # Analyze results
        success = True
        issues = []
        
        # Check funding type expectations
        if 'expected_type' in test_case:
            actual_type = funding_info.get('funding_type')
            if actual_type != test_case['expected_type']:
                success = False
                issues.append(f"Expected funding_type '{test_case['expected_type']}', got '{actual_type}'")
        
        # Check market sizing expectations
        if test_case.get('expected_market_data'):
            market_sizing = funding_info.get('market_sizing', {})
            if not market_sizing:
                success = False
                issues.append("Expected market sizing data, but none found")
        
        # Check funding mentions
        if test_case.get('expected_funding_mentions'):
            has_funding_info = (
                funding_info.get('total_funding_pool') or
                funding_info.get('exact_amount_per_project') or
                (funding_info.get('min_amount_per_project') and funding_info.get('max_amount_per_project'))
            )
            if not has_funding_info:
                success = False
                issues.append("Expected funding information, but none extracted")
        
        # Display results
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"Result: {status}")
        
        if issues:
            for issue in issues:
                print(f"  - {issue}")
        
        # Show key extracted data
        key_data = {}
        if funding_info.get('funding_type'):
            key_data['funding_type'] = funding_info['funding_type']
        if funding_info.get('total_funding_pool'):
            key_data['total_funding_pool'] = funding_info['total_funding_pool']
        if funding_info.get('exact_amount_per_project'):
            key_data['exact_amount'] = funding_info['exact_amount_per_project']
        if funding_info.get('min_amount_per_project') and funding_info.get('max_amount_per_project'):
            key_data['amount_range'] = f"{funding_info['min_amount_per_project']}-{funding_info['max_amount_per_project']}"
        if funding_info.get('market_sizing'):
            key_data['market_sizing'] = len(funding_info['market_sizing'])
        if funding_info.get('target_audience'):
            key_data['target_audience'] = funding_info['target_audience']
        if funding_info.get('ai_subsectors'):
            key_data['ai_subsectors'] = funding_info['ai_subsectors']
        
        if key_data:
            print(f"  Extracted: {key_data}")
        
        results.append({
            "test_case": test_case['name'],
            "success": success,
            "issues": issues,
            "extracted_data": key_data,
            "full_extraction": funding_info
        })
    
    # Summary
    passed = len([r for r in results if r['success']])
    total = len(results)
    
    print(f"\n📊 EXTRACTION TEST SUMMARY")
    print("=" * 50)
    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed < total:
        print(f"\n⚠️  Failed Tests:")
        for result in results:
            if not result['success']:
                print(f"  - {result['test_case']}: {', '.join(result['issues'])}")
    
    # Save detailed results
    with open('funding_extraction_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: funding_extraction_test_results.json")
    
    # Performance recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"  1. Patterns working well: Total pool, exact amount, range patterns")
    print(f"  2. Market sizing extraction: {'✅ Working' if any(r.get('extracted_data', {}).get('market_sizing') for r in results) else '⚠️  Needs improvement'}")
    print(f"  3. Target audience detection: {'✅ Working' if any(r.get('extracted_data', {}).get('target_audience') for r in results) else '⚠️  Needs improvement'}")
    
    return results


if __name__ == "__main__":
    test_funding_extraction()
