import re
import time
from datetime import datetime
from PIL import Image, ImageDraw
import json
from collections import defaultdict

class AdvancedComplianceEngine:
    def __init__(self):
        self.hard_rules = self.load_tesco_guidelines()
        self.violation_history = []
    
    def load_tesco_guidelines(self):
        """Load ALL Tesco guidelines from Appendix A and B EXACTLY as per problem statement"""
        return {
            # Appendix B - EXACT forbidden terms from problem statement
            "forbidden_claims": [
                # T&Cs - HARD FAIL (Appendix B)
                "terms", "conditions", "t&c", "t&cs", "terms and conditions", "conditions apply",
                
                # Competitions - HARD FAIL (Appendix B)
                "win", "winner", "winning", "prize", "competition", "contest", "raffle", "lottery",
                "gamble", "bet", "chance to win", "free entry", "entry", "draw", "win a", "winning",
                
                # Sustainability (Green Claims) - HARD FAIL (Appendix B)
                "eco", "ecological", "sustainable", "sustainability", "green", "environmental",
                "planet", "carbon", "zero waste", "recyclable", "biodegradable", "compostable",
                "organic", "natural", "environment", "earth", "eco-friendly", "environmentally",
                
                # Charity Partnerships - HARD FAIL (Appendix B)
                "charity", "donation", "proceeds", "fundraising", "support", "help", "give back",
                "community", "fund", "raise money", "donate", "charitable", "proceeds to",
                
                # Price Call-outs - HARD FAIL (Appendix B)
                "£", "$", "price", "cost", "only", "just", "value", "cheap", "inexpensive",
                "affordable", "budget", "discount", "sale", "clearance", "bargain", "deal",
                "offer", "special offer", "limited time", "act now", "buy now", "save",
                "reduced", "markdown", "price drop", "now only", "was £", "was $",
                
                # Money-Back Guarantees - HARD FAIL (Appendix B)
                "money-back", "guarantee", "warranty", "refund", "risk-free", "certain",
                "guaranteed", "money back", "satisfaction guaranteed",
                
                # Claims indicators - HARD FAIL (Appendix B)
                "*", "†", "‡", "§", "¶", "※", "footnote", "see below", "survey claims",
                "clinical", "proven", "studies show", "research shows", "tests prove",
                "clinically proven", "scientifically proven", "doctor recommended",
                
                # Health/Medical claims - HARD FAIL
                "healthy", "healthier", "health", "cure", "treatment", "medical", "clinical", 
                "doctor", "physician", "wellness", "benefits", "good for you", "better for you",
                "improve", "improves", "performance", "energy", "nutritious", "vitamin",
                "mineral", "supplement", "immune", "detox", "cleanse", "boosts", "enhances",
                
                # Superlatives and absolute claims - HARD FAIL
                "best", "perfect", "ideal", "ultimate", "premium", "luxury", "superior",
                "excellent", "amazing", "incredible", "fantastic", "number one", "#1",
                "top", "finest", "greatest", "most", "leading", "unbeatable", "unmatched",
                
                # Free offers - HARD FAIL
                "free", "freebie", "complimentary", "gratis", "no charge", "free of charge",
                "free gift", "free sample",
                
                # Scarcity and urgency - HARD FAIL
                "limited", "limited edition", "while stocks last", "last chance", "final",
                "ending soon", "almost gone", "selling fast", "hurry", "limited supply",
                
                # Exclusive claims (unless using approved tag)
                "exclusive", "only at", "unique", "special", "only here", "only available at",
                
                # VIOLENCE AND CRIME - NEW ENHANCED DETECTION
                "murder", "kill", "killing", "death", "dead", "die", "dying", "violence", "violent",
                "weapon", "gun", "knife", "attack", "assault", "harm", "harmful", "danger", "dangerous",
                "unsafe", "threat", "threatening", "brutal", "brutality", "aggression", "aggressive",
                "fight", "fighting", "war", "battle", "combat", "shoot", "shooting", "stab", "stabbing",
                "hit", "hitting", "punch", "punching", "beat", "beating", "abuse", "abusive",
                
                # ILLEGAL ACTIVITIES - NEW ENHANCED DETECTION
                "illegal", "crime", "criminal", "felony", "theft", "steal", "stealing", "robbery",
                "burglary", "fraud", "scam", "cheat", "cheating", "deceive", "deception", "mislead",
                "false", "fake", "counterfeit", "forgery", "pirate", "piracy", "black market",
                "contraband", "smuggle", "smuggling", "bribe", "bribery", "corruption", "corrupt",
                
                # DRUGS AND SUBSTANCE ABUSE - NEW ENHANCED DETECTION
                "drug", "drugs", "narcotic", "cocaine", "heroin", "marijuana", "cannabis", "opioid",
                "meth", "methamphetamine", "amphetamine", "ecstasy", "mdma", "lsd", "acid",
                "psychedelic", "hallucinogen", "stimulant", "depressant", "abuse", "addiction",
                "addictive", "intoxication", "intoxicated", "drunk", "drunkenness", "overdose",
                "withdrawal", "rehab", "rehabilitation", "substance", "narcotics",
                
                # MENTAL HEALTH - NEW ENHANCED DETECTION
                "suicide", "suicidal", "self-harm", "self-harming", "depression", "depressed",
                "anxiety", "anxious", "mental health", "mental illness", "psychiatric", "psychosis",
                "bipolar", "schizophrenia", "trauma", "traumatic", "ptsd", "breakdown", "psychology",
                "therapy", "therapist", "counseling", "counselor", "eating disorder", "anorexia",
                "bulimia", "self-injury", "cutting", "hopeless", "despair", "misery",
                
                # HATE SPEECH AND DISCRIMINATION - NEW ENHANCED DETECTION
                "hate", "hatred", "racism", "racist", "discrimination", "discriminatory", "prejudice",
                "biased", "bias", "offensive", "offend", "slur", "bigotry", "bigot", "xenophobia",
                "xenophobic", "homophobia", "homophobic", "transphobia", "transphobic", "sexism",
                "sexist", "misogyny", "misogynistic", "antisemitism", "anti-semitic", "islamophobia",
                "white supremacy", "supremacist", "nazi", "kkk", "ku klux klan", "extremist",
                
                # ADULT AND EXPLICIT CONTENT - NEW ENHANCED DETECTION
                "porn", "pornography", "pornographic", "xxx", "sex", "sexual", "sexy", "nude",
                "nudity", "naked", "explicit", "adult", "mature", "erotic", "erotica", "obscene",
                "obscenity", "vulgar", "vulgarity", "lewd", "indecent", "prostitute", "prostitution",
                "escort", "stripper", "stripping", "brothel", "orgy", "orgies", "masturbation",
                "fetish", "bdsm", "bondage", "dominance", "submission", "sadism", "masochism",
                
                # TERRORISM AND EXTREMISM - NEW ENHANCED DETECTION
                "terror", "terrorist", "terrorism", "extremist", "radical", "radicalization",
                "bomb", "bombing", "explosive", "explosion", "detonate", "detonation", "jihad",
                "jihadist", "isis", "isil", "al-qaeda", "taliban", "jihad", "suicide bomb",
                "suicide bombing", "martyr", "martyrdom", "jihad", "hijack", "hijacking",
                "hostage", "kidnap", "kidnapping", "beheading", "execution", "massacre",
                
                # GAMBLING AND BETTING - NEW ENHANCED DETECTION
                "gambling", "gamble", "bet", "betting", "wager", "wagering", "casino", "poker",
                "blackjack", "roulette", "slot machine", "slots", "lottery", "lotto", "bingo",
                "scratch card", "sports betting", "bookmaker", "bookie", "odds", "stakes",
                "jackpot", "payout", "winnings", "bookmaker", "bookie"
            ],
            
            # Appendix A - EXACT allowed tags from problem statement
            "allowed_tags": [
                "Only at Tesco",
                "Available at Tesco", 
                "Selected stores. While stocks last.",
                "Clubcard/app required. Ends DD/MM"
            ],
            
            # Appendix B - EXACT design rules from problem statement
            "design_rules": {
                "min_font_sizes": {
                    "headline": 20,    # Brand/social minimum - HARD FAIL
                    "subhead": 12,     # SAYS minimum - HARD FAIL
                    "drinkaware": 20   # Alcohol minimum - HARD FAIL
                },
                "safe_zones": {
                    "9:16": {"top": 200, "bottom": 250}  # HARD FAIL - Facebook/Instagram Stories only
                },
                "value_tile_rules": {
                    "no_overlap": True  # HARD FAIL - Content cannot overlay value tile
                },
                "packshot_rules": {
                    "max_count": 3,  # Appendix A
                    "min_gap_double_density": 24,   # HARD FAIL
                    "min_gap_single_density": 12,   # HARD FAIL
                }
            },
            
            # Appendix B - EXACT alcohol-specific rules from problem statement
            "alcohol_requirements": {
                "drinkaware_required": True,  # HARD FAIL
                "drinkaware_min_size": 20,    # HARD FAIL (12px for SAYS override)
                "colors": ["black", "white"], # HARD FAIL - all-black or all-white only
                "sufficient_contrast": True,  # HARD FAIL
                "forbidden_alcohol_terms": [
                    "enjoy more", "drink up", "celebrate with", "party", "cheers",
                    "get the party started", "perfect for parties", "social gathering",
                    "great for celebrations", "festive", "toast", "get drunk", "intoxicated",
                    "binge", "alcoholic", "alcoholism", "liquor", "spirits", "booze",
                    "shots", "chug", "hammered", "wasted", "plastered", "smashed"
                ]
            },
            
            # Appendix A - EXACT conditional rules from problem statement
            "conditional_rules": {
                "clubcard_requires_end_date": True,
                "lep_position_right": True,
                "pinterest_requires_tag": True,
                "creative_links_to_tesco_requires_tag": True,
                "creative_links_to_tesco_requires_value_tile": True
            }
        }
    
    def check_text_compliance(self, headline, subhead, product_category="general"):
        """Check text compliance with Appendix B HARD FAIL rules - EXACT problem statement implementation"""
        issues = []
        suggestions = []
        
        # Combine text for analysis
        text_to_check = f"{headline} {subhead}".lower()
        
        # HARD FAIL: Check for ALL forbidden terms from Appendix B
        for term in self.hard_rules["forbidden_claims"]:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_to_check, re.IGNORECASE):
                issues.append(f"HARD FAIL: '{term}' detected - {self.get_rule_description(term)}")
                alternative = self.get_compliant_alternative(term)
                if alternative:
                    suggestions.append(f"Replace '{term}' with: '{alternative}'")
        
        # Enhanced claim detection patterns
        claim_patterns = self._get_enhanced_claim_patterns()
        
        for pattern, message in claim_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                if message not in issues:  # Avoid duplicates
                    issues.append(f"HARD FAIL: {message}")
        
        # Special claim detection for asterisks and reference marks
        if any(char in headline + subhead for char in ['*', '†', '‡', '§', '¶', '※']):
            issues.append("HARD FAIL: Claim indicators (asterisks/reference marks) detected - indicates T&Cs/claims")
            suggestions.append("Remove all asterisks (*), daggers (†), and other reference marks")
        
        # Check for common claim phrases
        claim_phrases = [
            (r'\b(?:see|refer to|check)\s+(?:below|details|footnote|terms)', "'See below/details' reference detected"),
            (r'\b(?:subject to|according to)\s+(?:terms|conditions)', "Terms and conditions reference detected"),
            (r'\b(?:based on|according to)\s+(?:survey|research|study|test)', "Research/survey-based claim detected"),
            (r'\b(?:results?|outcomes?)\s+(?:show|prove|demonstrate|indicate)', "Result-based claim detected"),
            (r'\b(?:clinical|scientific|medical)\s+(?:evidence|proof|study|research)', "Scientific/clinical claim detected"),
            (r'\b(?:proven|tested|verified)\s+(?:by|to|that)', "Verification/proof claim detected"),
            (r'\b(?:guarantee|warranty)\s+(?:period|coverage|terms)', "Guarantee/warranty terms detected"),
            (r'\b(?:limited|while)\s+stocks?\s+last', "Scarcity claim detected"),
            (r'\b(?:act|buy)\s+now\b', "Urgency claim detected"),
            (r'\b(?:hurry|quick|fast)\b.*\b(?:sale|offer|deal)', "Urgency claim detected"),
        ]
        
        for pattern, message in claim_phrases:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                if f"HARD FAIL: {message}" not in issues:
                    issues.append(f"HARD FAIL: {message}")
        
        # HARD FAIL: Alcohol-specific checks (EXACT from problem statement)
        if product_category.lower() == "alcohol":
            alcohol_issues = self._check_alcohol_compliance(text_to_check)
            issues.extend(alcohol_issues)
        
        # HARD FAIL: Enhanced sensitive content checks
        sensitive_issues = self._check_sensitive_content(text_to_check)
        issues.extend(sensitive_issues)
        
        return {
            "approved": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "checks_performed": len(self.hard_rules["forbidden_claims"]) + len(claim_patterns) + len(claim_phrases),
            "product_category": product_category
        }
    
    def _get_enhanced_claim_patterns(self):
        """Get comprehensive claim detection patterns"""
        return [
            # T&Cs and reference patterns
            (r'\*', "Asterisk detected - indicates claims/T&Cs"),
            (r'†|‡|§|¶|※', "Reference symbol detected - indicates claims/T&Cs"),
            (r'\bfootnote\b', "Footnote reference detected"),
            (r'\bsee\s+below\b', "'See below' reference detected"),
            (r'\bdetails?\s+below\b', "'Details below' reference detected"),
            (r'\bfine\s+print\b', "Fine print reference detected"),
            (r'\bterms?\s+and?\s+conditions?\b', "Terms and conditions mentioned"),
            (r'\bt&c\b', "T&C abbreviation detected"),
            (r'\bt&cs\b', "T&Cs abbreviation detected"),
            
            # Survey and research claims
            (r'\bsurvey\b.*\bclaims?\b', "Survey claims detected"),
            (r'\bresearch\b.*\bshows?\b', "Research-based claims detected"),
            (r'\bstudies?\b.*\bshow\b', "Study-based claims detected"),
            (r'\btests?\b.*\bprove\b', "Test-based claims detected"),
            (r'\bclinical\b.*\bproven\b', "Clinical proof claims detected"),
            (r'\bscientifically\b.*\bproven\b', "Scientific proof claims detected"),
            (r'\bdoctor\b.*\brecommended\b', "Medical endorsement detected"),
            (r'\bexpert\b.*\bapproved\b', "Expert approval claim detected"),
            
            # Competition patterns
            (r'\bwin\b.*\b(free|prize)\b', "Competition language detected"),
            (r'\benter\b.*\b(competition|contest|raffle|draw)\b', "Competition entry detected"),
            (r'\bchance\b.*\bwin\b', "Competition chance detected"),
            (r'\bfree\s+entry\b', "Free entry competition detected"),
            (r'\bprize\s+draw\b', "Prize draw detected"),
            (r'\blottery\b', "Lottery/gambling detected"),
            (r'\bgambl', "Gambling content detected"),
            (r'\bbet\b', "Betting content detected"),
            
            # Price patterns
            (r'£\d+', "Price mention in copy"),
            (r'\$\d+', "Price mention in copy"),
            (r'\b\d+%\s*off\b', "Percentage discount detected"),
            (r'\bdiscount\b.*\bcode\b', "Discount code mentioned"),
            (r'\bsale\b.*\bprice\b', "Sale price mentioned"),
            (r'\bwas\s+£', "Previous price mentioned"),
            (r'\bnow\s+£', "Current price mentioned"),
            
            # Sustainability/green claims
            (r'\beco-?friendly\b', "Eco-friendly claim detected"),
            (r'\benvironmentally\s+friendly\b', "Environmentally friendly claim detected"),
            (r'\bgreen\s+product\b', "Green product claim detected"),
            (r'\bsustainable\b.*\bproduct\b', "Sustainable product claim detected"),
            (r'\bzero\s+waste\b', "Zero waste claim detected"),
            (r'\bcarbon\s+neutral\b', "Carbon neutral claim detected"),
            
            # Charity claims
            (r'\bcharity\b.*\bpartnership\b', "Charity partnership claim detected"),
            (r'\bdonation\b.*\bpurchase\b', "Donation per purchase claim detected"),
            (r'\bproceeds\b.*\bcharity\b', "Proceeds to charity claim detected"),
            (r'\bsupport\b.*\bcharity\b', "Charity support claim detected"),
            
            # Guarantee claims
            (r'\bmoney-?back\b.*\bguarantee\b', "Money-back guarantee detected"),
            (r'\bsatisfaction\s+guaranteed\b', "Satisfaction guarantee detected"),
            (r'\brisk-?free\b.*\btrial\b', "Risk-free trial detected"),
            (r'\bno\s+questions\s+asked\b', "No questions asked refund detected"),
            
            # Health claims
            (r'\bhealthy\b.*\bchoice\b', "Healthy choice claim detected"),
            (r'\bgood\s+for\s+you\b', "Health benefit claim detected"),
            (r'\bbenefits\b.*\bhealth\b', "Health benefits claim detected"),
            (r'\bimproves\b.*\bhealth\b', "Health improvement claim detected"),
            (r'\bboosts\b.*\bimmunity\b', "Immunity boost claim detected"),
            
            # Superlative claims
            (r'\bbest\b.*\bin\b.*\bworld\b', "World's best claim detected"),
            (r'\bnumber\s+one\b', "Number one claim detected"),
            (r'\btop\s+rated\b', "Top rated claim detected"),
            (r'\bpremium\s+quality\b', "Premium quality claim detected"),
            (r'\bluxury\b.*\bproduct\b', "Luxury product claim detected"),
            
            # Scarcity/urgency claims
            (r'\blimited\s+time\b', "Limited time offer detected"),
            (r'\bwhile\s+stocks\s+last\b', "While stocks last claim detected"),
            (r'\blast\s+chance\b', "Last chance claim detected"),
            (r'\bending\s+soon\b', "Ending soon claim detected"),
            (r'\bhurry\b.*\boffer\b', "Hurry offer detected"),
            
            # Exclusive claims
            (r'\bexclusive\b.*\boffer\b', "Exclusive offer detected"),
            (r'\bonly\s+at\b.*\btesco\b', "Only at Tesco claim (use approved tag instead)"),
            (r'\bunique\b.*\bopportunity\b', "Unique opportunity claim detected"),
        ]
    
    def _check_alcohol_compliance(self, text):
        """Check alcohol-specific compliance issues"""
        issues = []
        
        # Health claims for alcohol
        health_patterns = [
            (r'\bhealthy\b', "Health claim for alcohol"),
            (r'\bgood\s+for\s+you\b', "Health benefit claim"),
            (r'\bbenefits\b', "Benefit claims not allowed"),
            (r'\bimprove\b.*\bhealth\b', "Health improvement claim"),
            (r'\bmedical\b.*\bbenefits\b', "Medical benefits claim"),
            (r'\bwellness\b', "Wellness claim"),
            (r'\bnutritious\b', "Nutrition claim"),
            (r'\bvitamin\b', "Vitamin content claim"),
        ]
        
        for pattern, message in health_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} for alcohol (Appendix B)")
        
        # Encouragement patterns
        encouragement_patterns = [
            (r'\bcelebrate\b', "Encouragement of consumption"),
            (r'\bparty\b', "Social encouragement"),
            (r'\bdrink\s+up\b', "Encouragement of consumption"),
            (r'\benjoy\s+more\b', "Encouragement of consumption"),
            (r'\bcheers\b', "Encouragement of consumption"),
            (r'\btoast\b', "Encouragement of consumption"),
            (r'\bfestive\b', "Social encouragement"),
            (r'\bsocial\s+gathering\b', "Social encouragement"),
            (r'\bget\s+the\s+party\s+started\b', "Party encouragement"),
            (r'\bperfect\s+for\s+parties\b', "Party encouragement"),
            (r'\bget\s+drunk\b', "Encouragement of excessive consumption"),
            (r'\bintoxicated\b', "Encouragement of excessive consumption"),
            (r'\bbinge\b', "Encouragement of excessive consumption"),
            (r'\bhammered\b', "Encouragement of excessive consumption"),
            (r'\bwasted\b', "Encouragement of excessive consumption"),
            (r'\bsmashed\b', "Encouragement of excessive consumption"),
            (r'\bplastered\b', "Encouragement of excessive consumption"),
        ]
        
        for pattern, message in encouragement_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} not allowed for alcohol (Appendix B)")
        
        return issues
    
    def _check_sensitive_content(self, text):
        """Enhanced check for ALL types of sensitive and inappropriate content"""
        issues = []
        
        # VIOLENCE AND CRIME - Comprehensive detection
        violence_patterns = [
            (r'\bmurder\b', "Violent content (murder) detected"),
            (r'\bkill\b', "Violent content (kill) detected"),
            (r'\bkilling\b', "Violent content (killing) detected"),
            (r'\bdeath\b', "Violent/sensitive content (death) detected"),
            (r'\bdead\b', "Violent/sensitive content (dead) detected"),
            (r'\bdie\b', "Violent/sensitive content (die) detected"),
            (r'\bdying\b', "Violent/sensitive content (dying) detected"),
            (r'\bviolence\b', "Violent content detected"),
            (r'\bviolent\b', "Violent content detected"),
            (r'\bweapon\b', "Weapon/violent content detected"),
            (r'\bgun\b', "Weapon/violent content detected"),
            (r'\bknife\b', "Weapon/violent content detected"),
            (r'\battack\b', "Violent content detected"),
            (r'\bassault\b', "Violent content detected"),
            (r'\bharm\b', "Violent content detected"),
            (r'\bharmful\b', "Violent content detected"),
            (r'\bdanger\b', "Dangerous content detected"),
            (r'\bdangerous\b', "Dangerous content detected"),
            (r'\bunsafe\b', "Unsafe content detected"),
            (r'\bthreat\b', "Threatening content detected"),
            (r'\bthreatening\b', "Threatening content detected"),
            (r'\bbrutal\b', "Violent content detected"),
            (r'\bbrutality\b', "Violent content detected"),
            (r'\baggression\b', "Violent content detected"),
            (r'\baggressive\b', "Violent content detected"),
            (r'\bfight\b', "Violent content detected"),
            (r'\bfighting\b', "Violent content detected"),
            (r'\bwar\b', "Violent content detected"),
            (r'\bbattle\b', "Violent content detected"),
            (r'\bcombat\b', "Violent content detected"),
            (r'\bshoot\b', "Violent content detected"),
            (r'\bshooting\b', "Violent content detected"),
            (r'\bstab\b', "Violent content detected"),
            (r'\bstabbing\b', "Violent content detected"),
            (r'\bhit\b', "Violent content detected"),
            (r'\bhitting\b', "Violent content detected"),
            (r'\bpunch\b', "Violent content detected"),
            (r'\bpunching\b', "Violent content detected"),
            (r'\bbeat\b', "Violent content detected"),
            (r'\bbeating\b', "Violent content detected"),
            (r'\babuse\b', "Abusive/violent content detected"),
            (r'\babusive\b', "Abusive content detected"),
        ]
        
        for pattern, message in violence_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Violent/inappropriate content")
        
        # ILLEGAL ACTIVITIES - Comprehensive detection
        illegal_patterns = [
            (r'\billegal\b', "Illegal activity reference detected"),
            (r'\bcrime\b', "Criminal activity reference detected"),
            (r'\bcriminal\b', "Criminal activity reference detected"),
            (r'\bfelony\b', "Criminal activity reference detected"),
            (r'\btheft\b', "Criminal activity reference detected"),
            (r'\bsteal\b', "Criminal activity reference detected"),
            (r'\bstealing\b', "Criminal activity reference detected"),
            (r'\brobbery\b', "Criminal activity reference detected"),
            (r'\bburglary\b', "Criminal activity reference detected"),
            (r'\bfraud\b', "Fraudulent activity detected"),
            (r'\bscam\b', "Fraudulent activity detected"),
            (r'\bcheat\b', "Dishonest activity detected"),
            (r'\bcheating\b', "Dishonest activity detected"),
            (r'\bdeceive\b', "Dishonest activity detected"),
            (r'\bdeception\b', "Dishonest activity detected"),
            (r'\bmislead\b', "Dishonest activity detected"),
            (r'\bfalse\b', "False claims detected"),
            (r'\bfake\b', "Counterfeit/fake content detected"),
            (r'\bcounterfeit\b', "Counterfeit content detected"),
            (r'\bforgery\b', "Illegal activity detected"),
            (r'\bpirate\b', "Illegal activity detected"),
            (r'\bpiracy\b', "Illegal activity detected"),
            (r'\bblack market\b', "Illegal activity detected"),
            (r'\bcontraband\b', "Illegal activity detected"),
            (r'\bsmuggle\b', "Illegal activity detected"),
            (r'\bsmuggling\b', "Illegal activity detected"),
            (r'\bbribe\b', "Illegal activity detected"),
            (r'\bbribery\b', "Illegal activity detected"),
            (r'\bcorruption\b', "Illegal activity detected"),
            (r'\bcorrupt\b', "Illegal activity detected"),
        ]
        
        for pattern, message in illegal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Illegal/inappropriate content")
        
        # DRUGS AND SUBSTANCE ABUSE - Comprehensive detection
        drug_patterns = [
            (r'\bdrug\b', "Drug reference detected"),
            (r'\bdrugs\b', "Drug reference detected"),
            (r'\bnarcotic\b', "Drug reference detected"),
            (r'\bcocaine\b', "Illegal drug reference detected"),
            (r'\bheroin\b', "Illegal drug reference detected"),
            (r'\bmarijuana\b', "Drug reference detected"),
            (r'\bcannabis\b', "Drug reference detected"),
            (r'\bopioid\b', "Drug reference detected"),
            (r'\bmeth\b', "Illegal drug reference detected"),
            (r'\bmethamphetamine\b', "Illegal drug reference detected"),
            (r'\bamphetamine\b', "Drug reference detected"),
            (r'\becstasy\b', "Illegal drug reference detected"),
            (r'\bmdma\b', "Illegal drug reference detected"),
            (r'\blsd\b', "Illegal drug reference detected"),
            (r'\bacid\b', "Illegal drug reference detected"),
            (r'\bpsychedelic\b', "Drug reference detected"),
            (r'\bhallucinogen\b', "Drug reference detected"),
            (r'\bstimulant\b', "Drug reference detected"),
            (r'\bdepressant\b', "Drug reference detected"),
            (r'\babuse\b', "Substance abuse reference detected"),
            (r'\baddiction\b', "Addiction reference detected"),
            (r'\baddictive\b', "Addiction reference detected"),
            (r'\bintoxication\b', "Substance abuse reference detected"),
            (r'\bintoxicated\b', "Substance abuse reference detected"),
            (r'\bdrunk\b', "Substance abuse reference detected"),
            (r'\bdrunkenness\b', "Substance abuse reference detected"),
            (r'\boverdose\b', "Substance abuse reference detected"),
            (r'\bwithdrawal\b', "Substance abuse reference detected"),
            (r'\brehab\b', "Substance abuse reference detected"),
            (r'\brehabilitation\b', "Substance abuse reference detected"),
            (r'\bsubstance\b', "Substance abuse reference detected"),
            (r'\bnarcotics\b', "Drug reference detected"),
        ]
        
        for pattern, message in drug_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Drug/substance abuse content")
        
        # MENTAL HEALTH - Comprehensive detection
        mental_health_patterns = [
            (r'\bsuicide\b', "Suicide/self-harm content detected"),
            (r'\bsuicidal\b', "Suicide/self-harm content detected"),
            (r'\bself-harm\b', "Self-harm content detected"),
            (r'\bself-harming\b', "Self-harm content detected"),
            (r'\bdepression\b', "Mental health content detected"),
            (r'\bdepressed\b', "Mental health content detected"),
            (r'\banxiety\b', "Mental health content detected"),
            (r'\banxious\b', "Mental health content detected"),
            (r'\bmental health\b', "Mental health content detected"),
            (r'\bmental illness\b', "Mental health content detected"),
            (r'\bpsychiatric\b', "Mental health content detected"),
            (r'\bpsychosis\b', "Mental health content detected"),
            (r'\bbipolar\b', "Mental health content detected"),
            (r'\bschizophrenia\b', "Mental health content detected"),
            (r'\btrauma\b', "Mental health content detected"),
            (r'\btraumatic\b', "Mental health content detected"),
            (r'\bptsd\b', "Mental health content detected"),
            (r'\bbreakdown\b', "Mental health content detected"),
            (r'\bpsychology\b', "Mental health content detected"),
            (r'\btherapy\b', "Mental health content detected"),
            (r'\btherapist\b', "Mental health content detected"),
            (r'\bcounseling\b', "Mental health content detected"),
            (r'\bcounselor\b', "Mental health content detected"),
            (r'\beating disorder\b', "Mental health content detected"),
            (r'\banorexia\b', "Mental health content detected"),
            (r'\bbulimia\b', "Mental health content detected"),
            (r'\bself-injury\b', "Self-harm content detected"),
            (r'\bcutting\b', "Self-harm content detected"),
            (r'\bhopeless\b', "Mental health content detected"),
            (r'\bdespair\b', "Mental health content detected"),
            (r'\bmisery\b', "Mental health content detected"),
        ]
        
        for pattern, message in mental_health_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Mental health/sensitive content")
        
        # HATE SPEECH AND DISCRIMINATION - Comprehensive detection
        hate_patterns = [
            (r'\bhate\b', "Hate speech detected"),
            (r'\bhatred\b', "Hate speech detected"),
            (r'\bracism\b', "Racist content detected"),
            (r'\bracist\b', "Racist content detected"),
            (r'\bdiscrimination\b', "Discriminatory content detected"),
            (r'\bdiscriminatory\b', "Discriminatory content detected"),
            (r'\bprejudice\b', "Prejudiced content detected"),
            (r'\bbiased\b', "Biased content detected"),
            (r'\bbias\b', "Biased content detected"),
            (r'\boffensive\b', "Offensive content detected"),
            (r'\boffend\b', "Offensive content detected"),
            (r'\bslur\b', "Offensive content detected"),
            (r'\bbigotry\b', "Hate speech detected"),
            (r'\bbigot\b', "Hate speech detected"),
            (r'\bxenophobia\b', "Hate speech detected"),
            (r'\bxenophobic\b', "Hate speech detected"),
            (r'\bhomophobia\b', "Hate speech detected"),
            (r'\bhomophobic\b', "Hate speech detected"),
            (r'\btransphobia\b', "Hate speech detected"),
            (r'\btransphobic\b', "Hate speech detected"),
            (r'\bsexism\b', "Discriminatory content detected"),
            (r'\bsexist\b', "Discriminatory content detected"),
            (r'\bmisogyny\b', "Discriminatory content detected"),
            (r'\bmisogynistic\b', "Discriminatory content detected"),
            (r'\bantisemitism\b', "Hate speech detected"),
            (r'\banti-semitic\b', "Hate speech detected"),
            (r'\bislamophobia\b', "Hate speech detected"),
            (r'\bwhite supremacy\b', "Hate speech detected"),
            (r'\bsupremacist\b', "Hate speech detected"),
            (r'\bnazi\b', "Hate speech detected"),
            (r'\bkkk\b', "Hate speech detected"),
            (r'\bku klux klan\b', "Hate speech detected"),
            (r'\bextremist\b', "Extremist content detected"),
        ]
        
        for pattern, message in hate_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Hate speech/discriminatory content")
        
        # ADULT AND EXPLICIT CONTENT - Comprehensive detection
        adult_patterns = [
            (r'\bporn\b', "Pornographic content detected"),
            (r'\bpornography\b', "Pornographic content detected"),
            (r'\bpornographic\b', "Pornographic content detected"),
            (r'\bxxx\b', "Adult content detected"),
            (r'\bsex\b', "Sexual content detected"),
            (r'\bsexual\b', "Sexual content detected"),
            (r'\bsexy\b', "Sexual content detected"),
            (r'\bnude\b', "Sexual content detected"),
            (r'\bnudity\b', "Sexual content detected"),
            (r'\bnaked\b', "Sexual content detected"),
            (r'\bexplicit\b', "Explicit content detected"),
            (r'\badult\b', "Adult content detected"),
            (r'\bmature\b', "Adult content detected"),
            (r'\berotic\b', "Adult content detected"),
            (r'\berotica\b', "Adult content detected"),
            (r'\bobscene\b', "Obscene content detected"),
            (r'\bobscenity\b', "Obscene content detected"),
            (r'\bvulgar\b', "Vulgar content detected"),
            (r'\bvulgarity\b', "Vulgar content detected"),
            (r'\blewd\b', "Adult content detected"),
            (r'\bindecent\b', "Adult content detected"),
            (r'\bprostitute\b', "Adult content detected"),
            (r'\bprostitution\b', "Adult content detected"),
            (r'\bescort\b', "Adult content detected"),
            (r'\bstripper\b', "Adult content detected"),
            (r'\bstripping\b', "Adult content detected"),
            (r'\bbrothel\b', "Adult content detected"),
            (r'\borgy\b', "Adult content detected"),
            (r'\borgies\b', "Adult content detected"),
            (r'\bmasturbation\b', "Adult content detected"),
            (r'\bfetish\b', "Adult content detected"),
            (r'\bbdsm\b', "Adult content detected"),
            (r'\bbondage\b', "Adult content detected"),
            (r'\bdominance\b', "Adult content detected"),
            (r'\bsubmission\b', "Adult content detected"),
            (r'\bsadism\b', "Adult content detected"),
            (r'\bmasochism\b', "Adult content detected"),
        ]
        
        for pattern, message in adult_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Adult/explicit content")
        
        # TERRORISM AND EXTREMISM - Comprehensive detection
        terror_patterns = [
            (r'\bterror\b', "Terrorism content detected"),
            (r'\bterrorist\b', "Terrorism content detected"),
            (r'\bterrorism\b', "Terrorism content detected"),
            (r'\bextremist\b', "Extremist content detected"),
            (r'\bradical\b', "Extremist content detected"),
            (r'\bradicalization\b', "Extremist content detected"),
            (r'\bbomb\b', "Violent/terrorism content detected"),
            (r'\bbombing\b', "Violent/terrorism content detected"),
            (r'\bexplosive\b', "Violent/terrorism content detected"),
            (r'\bexplosion\b', "Violent/terrorism content detected"),
            (r'\bdetonate\b', "Violent/terrorism content detected"),
            (r'\bdetonation\b', "Violent/terrorism content detected"),
            (r'\bjihad\b', "Extremist content detected"),
            (r'\bjihadist\b', "Extremist content detected"),
            (r'\bisis\b', "Terrorist organization detected"),
            (r'\bisil\b', "Terrorist organization detected"),
            (r'\bal-qaeda\b', "Terrorist organization detected"),
            (r'\btaliban\b', "Terrorist organization detected"),
            (r'\bsuicide bomb\b', "Terrorism content detected"),
            (r'\bsuicide bombing\b', "Terrorism content detected"),
            (r'\bmartyr\b', "Extremist content detected"),
            (r'\bmartyrdom\b', "Extremist content detected"),
            (r'\bhijack\b', "Terrorism content detected"),
            (r'\bhijacking\b', "Terrorism content detected"),
            (r'\bhostage\b', "Terrorism content detected"),
            (r'\bkidnap\b', "Terrorism content detected"),
            (r'\bkidnapping\b', "Terrorism content detected"),
            (r'\bbeheading\b', "Violent/terrorism content detected"),
            (r'\bexecution\b', "Violent/terrorism content detected"),
            (r'\bmassacre\b', "Violent/terrorism content detected"),
        ]
        
        for pattern, message in terror_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Terrorism/extremist content")
        
        # GAMBLING AND BETTING - Comprehensive detection
        gambling_patterns = [
            (r'\bgambling\b', "Gambling content detected"),
            (r'\bgamble\b', "Gambling content detected"),
            (r'\bbet\b', "Gambling content detected"),
            (r'\bbetting\b', "Gambling content detected"),
            (r'\bwager\b', "Gambling content detected"),
            (r'\bwagering\b', "Gambling content detected"),
            (r'\bcasino\b', "Gambling content detected"),
            (r'\bpoker\b', "Gambling content detected"),
            (r'\bblackjack\b', "Gambling content detected"),
            (r'\broulette\b', "Gambling content detected"),
            (r'\bslot machine\b', "Gambling content detected"),
            (r'\bslots\b', "Gambling content detected"),
            (r'\blottery\b', "Gambling content detected"),
            (r'\blotto\b', "Gambling content detected"),
            (r'\bbingo\b', "Gambling content detected"),
            (r'\bscratch card\b', "Gambling content detected"),
            (r'\bsports betting\b', "Gambling content detected"),
            (r'\bbookmaker\b', "Gambling content detected"),
            (r'\bbookie\b', "Gambling content detected"),
            (r'\bodds\b', "Gambling content detected"),
            (r'\bstakes\b', "Gambling content detected"),
            (r'\bjackpot\b', "Gambling content detected"),
            (r'\bpayout\b', "Gambling content detected"),
            (r'\bwinnings\b', "Gambling content detected"),
        ]
        
        for pattern, message in gambling_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"HARD FAIL: {message} - Gambling content")
        
        return issues
    
    def get_rule_description(self, term):
        """Get the specific rule description for forbidden terms"""
        rule_descriptions = {
            "win": "Competitions not allowed - No mechanism for verifying claims",
            "prize": "Competitions not allowed - No mechanism for verifying claims",
            "competition": "Competitions not allowed - No mechanism for verifying claims",
            "eco": "Sustainability claims not allowed",
            "sustainable": "Sustainability claims not allowed", 
            "green": "Sustainability claims not allowed",
            "charity": "Charity partnerships not allowed",
            "donation": "Charity partnerships not allowed",
            "£": "Price call-outs not allowed in copy",
            "$": "Price call-outs not allowed in copy", 
            "price": "Price call-outs not allowed in copy",
            "discount": "Price call-outs not allowed in copy",
            "money-back": "Money-back guarantees not allowed",
            "guarantee": "Money-back guarantees not allowed",
            "*": "Claims/T&Cs not allowed - Cannot police claims for self-serve media",
            "terms": "Claims/T&Cs not allowed - Cannot police claims for self-serve media",
            "healthy": "Health claims not allowed - especially for alcohol products",
            "best": "Superlative claims not allowed",
            "free": "Free offers not allowed",
            "limited": "Scarcity/urgency claims not allowed",
            "murder": "Violent/inappropriate content not allowed",
            "kill": "Violent/inappropriate content not allowed",
            "lottery": "Gambling content not allowed",
            "gamble": "Gambling content not allowed",
            "drug": "Drug/substance references not allowed",
            "alcohol": "Alcohol encouragement not allowed",
            "suicide": "Mental health/sensitive content not allowed",
            "racism": "Hate speech/discriminatory content not allowed",
            "porn": "Adult/explicit content not allowed",
            "terror": "Terrorism/extremist content not allowed",
            "bomb": "Violent/terrorism content not allowed",
        }
        return rule_descriptions.get(term, "Not allowed per Appendix B guidelines")
    
    def get_compliant_alternative(self, forbidden_term):
        """Provide compliant alternatives for forbidden terms"""
        alternatives = {
            "win": "discover",
            "free": "",
            "discount": "value",
            "sale": "selection",
            "healthy": "enjoyable",
            "best": "excellent",
            "guarantee": "quality",
            "£": "",
            "$": "",
            "eco": "",
            "sustainable": "quality",
            "charity": "",
            "prize": "opportunity",
            "organic": "",
            "natural": "",
            "limited": "",
            "exclusive": "",
            "only at": "available",
            "money-back": "",
            "save": "",
            "murder": "",
            "kill": "",
            "lottery": "",
            "gamble": "",
            "drug": "",
            "alcohol": "beverage",
            "suicide": "",
            "racism": "",
            "porn": "",
            "terror": "",
            "bomb": "",
        }
        return alternatives.get(forbidden_term, "")
    
    def validate_creative_design(self, creative_data, format_name):
        """Validate creative design against Appendix A & B guidelines - EXACT problem statement"""
        issues = []
        warnings = []
        hard_fails = []
        
        # Appendix B HARD FAIL: Safe zones for 9:16 format (Facebook/Instagram Stories ONLY)
        if "1080x1920" in format_name or "9:16" in format_name:
            hard_fails.append("HARD FAIL: 9:16 format - leave 200px top and 250px bottom free from text/logos")
        
        # Appendix B HARD FAIL: Font size requirements
        min_sizes = self.hard_rules["design_rules"]["min_font_sizes"]
        hard_fails.append(f"HARD FAIL: Minimum font sizes - Headline ≥{min_sizes['headline']}px, Subhead ≥{min_sizes['subhead']}px")
        
        # Appendix B HARD FAIL: Alcohol-specific requirements
        if creative_data.get('product_category', '').lower() == 'alcohol':
            if not creative_data.get('include_drinkaware', False):
                hard_fails.append("HARD FAIL: Drinkaware required for alcohol campaigns")
            else:
                # Check Drinkaware specific requirements
                hard_fails.extend([
                    "HARD FAIL: Drinkaware - sufficient contrast from background",
                    "HARD FAIL: Drinkaware - all-black or all-white only", 
                    "HARD FAIL: Drinkaware - minimum 20px height (12px for SAYS)"
                ])
        
        # Appendix A: Value tile validation
        if creative_data.get('value_tile_type') and creative_data.get('value_tile_type') != 'None':
            # Appendix B HARD FAIL: No overlapping elements
            hard_fails.append("HARD FAIL: Content cannot overlay value tile")
            
            # Appendix A: Position validation
            if creative_data.get('value_tile_type') == 'Everyday Low Price':
                warnings.append("LEP must be positioned to right of packshot")
        
        # Appendix A HARD FAIL: Clubcard end date validation
        if creative_data.get('value_tile_type') == 'Clubcard Price':
            if not creative_data.get('clubcard_end_date'):
                hard_fails.append("HARD FAIL: End date (DD/MM) required for Clubcard Price tiles")
            else:
                # Validate DD/MM format
                end_date = creative_data.get('clubcard_end_date', '')
                if not re.match(r'^\d{2}/\d{2}$', end_date):
                    hard_fails.append("HARD FAIL: Clubcard end date must be in DD/MM format (e.g., 23/06)")
        
        # Appendix A & B: Tag validation
        if creative_data.get('creative_links_to_tesco', True):
            if not creative_data.get('tag_type') or creative_data.get('tag_type') == 'None':
                hard_fails.append("HARD FAIL: Tesco tag required when creative links to Tesco")
            else:
                allowed_tags = self.hard_rules["allowed_tags"]
                if creative_data.get('tag_type') not in allowed_tags:
                    hard_fails.append("HARD FAIL: Only approved Tesco tags allowed")
        
        # Appendix A: Packshot validation
        packshots = creative_data.get('packshots', [])
        if len(packshots) == 0:
            hard_fails.append("HARD FAIL: At least one packshot required - lead product required")
        elif len(packshots) > 3:
            hard_fails.append("HARD FAIL: Maximum 3 packshots allowed")
        
        # Appendix B HARD FAIL: Packshot positioning and safe zones
        if len(packshots) > 0:
            hard_fails.extend([
                "HARD FAIL: Packshot positioning - closest element to CTA",
                "HARD FAIL: Packshot safe zone - minimum gap requirements"
            ])
        
        # Appendix A: CTA validation
        if creative_data.get('cta'):
            hard_fails.append("HARD FAIL: No CTA allowed in creatives")
        
        return {
            "valid": len(hard_fails) == 0,
            "issues": issues + hard_fails + warnings,
            "warnings": warnings,
            "hard_fails": hard_fails
        }
    
    def full_creative_audit(self, creative_data, format_name):
        """Complete creative audit with detailed Appendix A & B reporting"""
        text_audit = self.check_text_compliance(
            creative_data.get('headline', ''),
            creative_data.get('subhead', ''),
            creative_data.get('product_category', 'general')
        )
        
        design_audit = self.validate_creative_design(creative_data, format_name)
        
        all_hard_fails = text_audit["issues"] + design_audit["hard_fails"]
        passed = len(all_hard_fails) == 0
        
        # Calculate compliance score (0-100)
        total_checks = text_audit["checks_performed"] + len(design_audit["issues"])
        failed_checks = len(all_hard_fails)
        score = max(0, 100 - (failed_checks * 10))
        
        return {
            "overall_assessment": {
                "passed": passed,
                "score": score,
                "grade": "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F",
                "message": "100% Appendix A & B Compliant" if passed else "HARD FAIL: Cannot generate"
            },
            "text_compliance": text_audit,
            "design_compliance": design_audit,
            "hard_fails": all_hard_fails,
            "warnings": design_audit["warnings"],
            "recommendations": text_audit["suggestions"]
        }
    
    def check_safe_zones(self, format_name, element_positions):
        """Check 9:16 safe zone compliance - Appendix B HARD FAIL"""
        issues = []
        
        # ONLY apply to Facebook/Instagram Stories 1080x1920px - 9:16 Ratio
        if "1080x1920" in format_name or "9:16" in format_name:
            safe_top = 200
            safe_bottom = 250
            
            for element, position in element_positions.items():
                y_position = position.get('y', 0)
                height = position.get('height', 0)
                
                # Check top safe zone
                if y_position < safe_top:
                    issues.append(f"HARD FAIL: {element} violates top 200px safe zone")
                
                # Check bottom safe zone
                if y_position + height > (1080 - safe_bottom):
                    issues.append(f"HARD FAIL: {element} violates bottom 250px safe zone")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues
        }
    
    def analyze_headline_subhead(self, headline, subhead, product_category):
        """Comprehensive analysis of headline and subhead for compliance"""
        analysis = {
            "headline_issues": [],
            "subhead_issues": [],
            "recommendations": [],
            "compliance_score": 100
        }
        
        full_text = f"{headline} {subhead}".lower()
        
        # Use the enhanced claim detection from check_text_compliance
        compliance_result = self.check_text_compliance(headline, subhead, product_category)
        
        # Convert issues to analysis format
        for issue in compliance_result["issues"]:
            analysis["headline_issues"].append(issue)
            analysis["compliance_score"] -= 10
        
        # Provide recommendations for improvement
        if analysis["compliance_score"] < 100:
            analysis["recommendations"].extend([
                "Remove all claim indicators like asterisks (*) and references",
                "Avoid price mentions in headline/subhead",
                "Use clear, benefit-oriented language without superlatives",
                "Ensure high contrast between text and background",
                "Remove any T&Cs, competition, or guarantee language",
                "Avoid sustainability, charity, or health claims",
                "Remove any violent, illegal, or inappropriate content",
                "Avoid references to drugs, alcohol encouragement, or gambling",
                "Remove hate speech, discriminatory, or offensive content",
                "Avoid adult, explicit, or sexual content",
                "Remove terrorism, extremist, or violent content",
                "Avoid mental health or sensitive topic references"
            ])
        
        # Ensure score doesn't go below 0
        analysis["compliance_score"] = max(0, analysis["compliance_score"])
        
        return analysis
    
    def log_violation(self, creative_data, issues, format_name):
        """Log compliance violations for analytics"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "creative_data": creative_data,
            "format": format_name,
            "issues": issues,
            "product_category": creative_data.get('product_category', 'general')
        }
        self.violation_history.append(violation)
        
        return violation