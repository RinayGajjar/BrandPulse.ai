import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from groq import Groq
import time
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from pathlib import Path

# Load environment variables
def load_env():
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY in environment variables")
    return api_key

# Initialize Groq
try:
    groq_client = Groq(api_key=load_env())  # Ensure only valid arguments are passed
except TypeError as e:
    raise ValueError(f"Error initializing Groq client: {str(e)}")
except Exception as e:
    raise ValueError(f"Unexpected error initializing Groq client: {str(e)}")

if not groq_client.api_key:
    raise ValueError("Missing GROQ_API_KEY in environment variables")

def init_streamlit():
    st.set_page_config(page_title="BrandPulse AI", layout="wide")
    
    # Update custom CSS with theme adaptability
    st.markdown("""
    <style>
    /* Color Palette Variables */
    :root {
        /* Dark theme colors */
        --dark-bg: #1E1E1E;
        --dark-card: rgba(42, 42, 74, 0.95);
        --dark-text: #e6d5c9;
        
        /* Light theme colors */
        --light-bg: #f8f9fa;
        --light-card: rgba(255, 255, 255, 0.95);
        --light-text: #2c1810;
        
        /* Common colors */
        --accent: #c68f65;
        --accent-dark: #8b4513;
        --accent-light: #d4a76a;
    }
    
    /* Theme-adaptive styles */
    .stApp {
        transition: all 0.3s ease;
    }
    
    /* Dark theme (default) */
    .stApp {
        background-image: linear-gradient(rgba(20, 14, 10, 0.75), rgba(30, 20, 15, 0.85)), 
            url('https://cdn.dribbble.com/userupload/36521817/file/original-f4f6de2ea8cb1e71ea872587ccb15c78.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: var(--dark-text);
    }
    
    /* Light theme adaptations */
    [data-theme="light"] .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(248, 249, 250, 0.9)), 
            url('https://cdn.dribbble.com/userupload/36521817/file/original-f4f6de2ea8cb1e71ea872587ccb15c78.jpg');
        color: var(--light-text);
    }
    
    /* Cards and Containers */
    .dashboard-card, .competitor-card {
        background: var(--dark-card);
        border: 1px solid var(--accent);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-theme="light"] .dashboard-card, 
    [data-theme="light"] .competitor-card {
        background: var(--light-card);
        border: 1px solid var(--accent-light);
        color: var(--light-text);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background-color: rgba(74, 52, 40, 0.1) !important;
        color: var(--dark-text) !important;
        border: 2px solid var(--accent-dark) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-theme="light"] .stTextInput > div > div > input,
    [data-theme="light"] .stNumberInput > div > div > input,
    [data-theme="light"] .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: var(--light-text) !important;
        border-color: var(--accent) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent), var(--accent-dark)) !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    [data-theme="light"] .stButton > button {
        background: linear-gradient(135deg, var(--accent-light), var(--accent)) !important;
        color: var(--light-text) !important;
    }
    
    /* Metric Boxes */
    .metric-box {
        background: rgba(108, 99, 255, 0.15);
        border: 1px solid var(--accent);
        transition: all 0.3s ease;
    }
    
    [data-theme="light"] .metric-box {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid var(--accent-light);
        color: var(--light-text);
    }
    
    /* Tables */
    .dataframe {
        background: var(--dark-card);
        color: var(--dark-text);
        transition: all 0.3s ease;
    }
    
    [data-theme="light"] .dataframe {
        background: var(--light-card);
        color: var(--light-text);
    }
    
    /* Text and Headers */
    h1, h2, h3, h4, h5, h6, p {
        color: var(--dark-text);
        transition: all 0.3s ease;
    }
    
    [data-theme="light"] h1,
    [data-theme="light"] h2,
    [data-theme="light"] h3,
    [data-theme="light"] h4,
    [data-theme="light"] h5,
    [data-theme="light"] h6,
    [data-theme="light"] p {
        color: var(--light-text);
    }
    
    /* Progress Bars */
    .stProgress > div > div {
        background-color: var(--accent) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: transparent !important;
        color: var(--dark-text) !important;
    }
    
    [data-theme="light"] .streamlit-expanderHeader {
        color: var(--light-text) !important;
    }
    
    /* Clean, Professional Tab Styling */
    .stTabs {
        margin-top: 20px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 2px solid rgba(52, 152, 219, 0.2);
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        color: #ECF0F1 !important;
        background: transparent !important;
        border: none !important;
        position: relative;
        bottom: -2px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #3498DB !important;
    }

    .stTabs [aria-selected="true"] {
        color: #3498DB !important;
        border-bottom: 2px solid #3498DB !important;
        background: transparent !important;
    }

    /* Clean Tool Selection Area */
    .tool-selection {
        padding: 20px 0;
        margin-bottom: 20px;
        background: transparent;
    }

    /* Remove glass effect from content area */
    .tab-content {
        background: transparent;
        padding: 20px 0;
    }

    /* Light theme adjustments */
    [data-theme="light"] .stTabs [data-baseweb="tab"] {
        color: #2C3E50 !important;
    }

    [data-theme="light"] .stTabs [aria-selected="true"] {
        color: #3498DB !important;
    }

    /* Remove any remaining blur effects */
    .stTabs [data-baseweb="tab-panel"] {
        backdrop-filter: none !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("BrandPulse AI")

class MarketingAgencyAutomation:
    def __init__(self):
        self.groq = groq_client
        self.session = requests.Session()

    def _get_completion(self, prompt: str) -> str:
        try:
            completion = self.groq.chat.completions.create(
                model="mistral-saba-24b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return completion.choices[0].message.content
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return "Sorry, there was an error generating the content. Please try again later."

    def seo_optimizer(self, url: str, keywords: List[str]) -> Dict[str, Any]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ""
            meta_desc = soup.find("meta", {"name": "description"})
            meta_desc = meta_desc["content"] if meta_desc else ""
            h1_tags = [h1.text.strip() for h1 in soup.find_all("h1")]
            analysis_prompt = f"""
            Analyze this webpage SEO for:
            URL: {url}
            Title: {title}
            Meta Description: {meta_desc}
            H1 Tags: {', '.join(h1_tags)}
            Target Keywords: {', '.join(keywords)}
            Provide recommendations for:
            1. Title optimization
            2. Meta description improvements
            3. Content structure
            4. Keyword placement
            5. Technical SEO improvements
            """
            seo_analysis = self._get_completion(analysis_prompt)
            return {
                "url": url,
                "current_title": title,
                "current_meta": meta_desc,
                "current_h1": h1_tags,
                "recommendations": seo_analysis
            }
        except Exception as e:
            return {"error": str(e)}

    def competitor_watchdog(self, competitors: List[str], keywords: List[str]) -> Dict[str, Any]:
        competitor_data = {}
        for competitor in competitors:
            # First, get a quick summary
            summary_prompt = f"""
            Provide a concise 3-point summary of {competitor}'s key strengths and market positioning:
            1. Primary competitive advantage
            2. Target audience focus
            3. Market differentiation
            Keep each point brief and actionable.
            """
            quick_summary = self._get_completion(summary_prompt)
            
            # Main analysis prompt
            analysis_prompt = f"""
            Provide a detailed competitive analysis for {competitor} focusing on:
            1. Content Strategy:
               - Content types and formats used
               - Publishing frequency and consistency
               - Content quality and engagement metrics
               - Target audience alignment and reach
            
            2. Keyword Analysis:
               - Usage of target keywords: {', '.join(keywords)}
               - Keyword density and placement strategy
               - Related keywords and semantic relevance
               - Overall SEO optimization effectiveness
            
            3. Market Presence:
               - Brand positioning and market share
               - Unique selling propositions (USPs)
               - Customer engagement and loyalty
               - Brand authority and credibility indicators
            
            4. Competitive Advantages:
               - Key strengths and core competencies
               - Notable weaknesses and gaps
               - Market opportunities to exploit
               - Potential threats to address
            
            5. Actionable Recommendations:
               - Immediate actions (next 30 days):
                 * Specific tactical improvements
                 * Quick wins and low-hanging fruit
               - Strategic initiatives (next 90 days):
                 * Long-term competitive advantages
                 * Market positioning improvements
               - Resource allocation suggestions:
                 * Required investments
                 * Expected outcomes
            
            Format each section with clear bullet points and specific examples.
            """
            competitor_analysis = self._get_completion(analysis_prompt)
            
            # Metrics analysis
            metrics_prompt = f"""
            Based on the website {competitor}, provide detailed metrics with justification:
            1. Content Quality Score (0-100):
               - Writing quality
               - Visual appeal
               - User engagement
            
            2. Keyword Optimization Level (0-100):
               - Keyword relevance
               - Content optimization
               - Technical SEO
            
            3. Market Position Strength (0-100):
               - Brand authority
               - Market share
               - Competitive advantage
            
            4. Brand Authority Score (0-100):
               - Industry presence
               - Social proof
               - Thought leadership
            
            For each metric, provide a specific score and brief justification.
            """
            metrics_analysis = self._get_completion(metrics_prompt)
            
            competitor_data[competitor] = {
                "quick_summary": quick_summary,
                "analysis": competitor_analysis,
                "metrics": metrics_analysis
            }
        return competitor_data

    def post_creator(self, topic: str, platform: str, tone: str = "professional") -> Dict[str, Any]:
        content_prompt = f"""
        Create a {platform} post about {topic} with a {tone} tone.
        Include:
        1. Main post content
        2. Relevant hashtags
        3. Call to action
        4. Best posting time recommendation
        """
        content = self._get_completion(content_prompt)
        return {"platform": platform, "content": content, "topic": topic, "created_at": datetime.now().isoformat()}

    def smart_email_manager(self, campaign_type: str, audience: List[Dict[str, Any]]) -> Dict[str, Any]:
        email_templates = {}
        for segment in audience:
            email_prompt = f"""
            Create an email campaign for:
            Campaign Type: {campaign_type}
            Audience Segment: {segment}
            Include:
            1. Subject line options
            2. Email body
            3. Call to action
            4. Personalization elements
            """
            email_content = self._get_completion(email_prompt)
            email_templates[segment["segment_name"]] = {
                "content": email_content,
                "subject_lines": self.generate_subject_lines(campaign_type, segment),
                "send_time": self.optimize_send_time(segment)
            }
        return email_templates

    def generate_subject_lines(self, campaign_type: str, segment: Dict[str, Any]) -> List[str]:
        prompt = f"Generate 5 engaging subject lines for {campaign_type} campaign targeting {segment['segment_name']}"
        return self._get_completion(prompt).split("\n")

    def optimize_send_time(self, segment: Dict[str, Any]) -> str:
        if segment.get("characteristics") == "first_time_buyers":
            return "14:00 PM"
        elif segment.get("characteristics") == "repeat_buyers":
            return "09:00 AM"
        return "10:00 AM"

def main():
    init_streamlit()
    
    try:
        marketing_system = MarketingAgencyAutomation()
    except ValueError as e:
        st.error(f"Error: {str(e)}")
        st.info("Please set up your API key in the .env file:\nGROQ_API_KEY=your_groq_api_key_here")
        return

    # Define tabs with cleaner styling
    tab1, tab2 = st.tabs(["Individual Analysis", "Comprehensive Analysis"])

    with tab1:
        st.subheader("Individual Analysis Tools")
        
        # Clean tool selection
        tool = st.selectbox("Select Analysis Tool:", 
                           ["SEO Optimizer", "Competitor Watchdog", "Post Creator", "Smart Email Manager"],
                           key="individual_tool")
        
        if tool == "SEO Optimizer":
            url = st.text_input("Website URL:", placeholder="https://example.com", key="ind_seo_url")
            keywords = st.text_input("Target Keywords:", placeholder="e.g., keyword1, keyword2", key="ind_seo_keywords")
            if st.button("Analyze SEO", key="ind_seo_button"):
                if url and keywords:
                    with st.spinner("Analyzing SEO..."):
                        keywords_list = [k.strip() for k in keywords.split(',')]
                        results = marketing_system.seo_optimizer(url, keywords_list)
                        if "error" in results:
                            st.error(f"SEO analysis failed: {results['error']}")
                        else:
                            st.subheader("SEO Analysis Results")
                            st.write(f"Title: {results['current_title']}")
                            st.write(f"Meta Description: {results['current_meta']}")
                            st.write(f"H1 Tags: {', '.join(results['current_h1'])}")
                            st.write("Recommendations:")
                            st.write(results['recommendations'])

        elif tool == "Competitor Watchdog":
            num_competitors = st.number_input("Number of competitors:", min_value=1, max_value=5, value=1, key="ind_comp_num")
            keywords = st.text_input("Keywords to track:", placeholder="e.g., keyword1, keyword2", key="ind_comp_keywords")
            competitors = []
            cols = st.columns(2)
            for i in range(int(num_competitors)):
                with cols[i % 2]:
                    comp_url = st.text_input(f"Competitor {i+1} URL:", key=f"ind_comp_url_{i}")
                    competitors.append(comp_url)
            if st.button("Analyze Competitors", key="ind_comp_button"):
                if all(competitors) and keywords:
                    with st.spinner("Analyzing competitors..."):
                        keywords_list = [k.strip() for k in keywords.split(',')]
                        results = marketing_system.competitor_watchdog(competitors, keywords_list)
                        
                        # Display detailed analysis for each competitor
                        for competitor, data in results.items():
                            st.markdown(f'<div class="competitor-card">', unsafe_allow_html=True)
                            st.subheader(f"Analysis for {competitor}")
                            
                            # Display metrics in a grid
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("### Key Metrics")
                                st.markdown(f'<div class="metric-box">{data["metrics"]}</div>', unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown("### Quick Summary")
                                st.markdown(f'<div class="metric-box">{data["quick_summary"]}</div>', unsafe_allow_html=True)
                            
                            # Parse and display analysis sections
                            analysis_text = data['analysis']
                            sections = {
                                "Content Strategy": "",
                                "Keyword Analysis": "",
                                "Market Presence": "",
                                "Competitive Advantages": "",
                                "Actionable Recommendations": ""
                            }
                            
                            # Parse sections
                            current_section = ""
                            current_content = []
                            
                            for line in analysis_text.split('\n'):
                                if any(section in line for section in sections.keys()):
                                    if current_section and current_content:
                                        sections[current_section] = '\n'.join(current_content)
                                        current_content = []
                                    current_section = next(section for section in sections.keys() if section in line)
                                elif current_section and line.strip():
                                    current_content.append(line)
                            
                            if current_section and current_content:
                                sections[current_section] = '\n'.join(current_content)
                            
                            # Display sections in tabs
                            analysis_tabs = st.tabs(list(sections.keys()))
                            
                            for tab, (section_name, content) in zip(analysis_tabs, sections.items()):
                                with tab:
                                    if content:
                                        st.markdown(content)
                                    else:
                                        st.markdown("*Analysis for this section is being generated...*")
                            
                            st.markdown("---")
                            st.markdown('</div>', unsafe_allow_html=True)

        elif tool == "Post Creator":
            content_type = st.selectbox("Content Type:", ["Social Media Post", "Blog Post", "Marketing Copy"], key="ind_content_type")
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input("Topic:", key="ind_content_topic")
                # Set platform based on content type
                if content_type == "Social Media Post":
                    platform = st.selectbox("Platform:", ["LinkedIn", "Twitter", "Facebook", "Instagram"], key="ind_content_platform")
                else:
                    platform = content_type  # Use content type as platform for Blog Post and Marketing Copy
            with col2:
                tone = st.selectbox("Tone:", ["Professional", "Casual", "Friendly", "Formal"], key="ind_content_tone")
            if st.button("Generate Content", key="ind_content_button"):
                if topic:
                    with st.spinner("Generating content..."):
                        post = marketing_system.post_creator(topic, platform, tone.lower())
                        st.subheader("Generated Content")
                        st.write(post['content'])

        elif tool == "Smart Email Manager":
            col1, col2, col3 = st.columns(3)
            with col1:
                brand_name = st.text_input("Brand Name:", key="ind_brand_name")
            with col2:
                industry = st.text_input("Industry:", key="ind_industry")
            with col3:
                campaign_type = st.selectbox("Campaign Type:", ["Welcome Series", "Promotional", "Newsletter", "Re-engagement", "Product Launch"], key="ind_email_type")
            num_segments = st.number_input("Number of segments:", min_value=1, max_value=3, value=1, key="ind_email_segments")
            segments = []
            for i in range(int(num_segments)):
                st.markdown(f"### Segment {i+1}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    name = st.text_input("Segment name:", key=f"ind_email_seg_name_{i}", placeholder="e.g., New Customers")
                with col2:
                    characteristics = st.selectbox("Characteristics:", ["First-time Buyers", "Repeat Customers", "VIP Members", "Inactive Users"], key=f"ind_email_seg_char_{i}")
                with col3:
                    previous_engagement = st.select_slider("Engagement Level:", options=["Very Low", "Low", "Medium", "High", "Very High"], key=f"ind_engagement_{i}")
                if name:
                    segments.append({"segment_name": name.strip(), "characteristics": characteristics, "engagement": previous_engagement})
            if st.button("Generate Campaign", key="ind_email_button"):
                if brand_name and segments:
                    with st.spinner("Crafting your email campaign..."):
                        results = marketing_system.smart_email_manager(campaign_type, segments)
                        for segment_name, email in results.items():
                            st.subheader(f"Campaign for {segment_name}")
                            st.write(email['content'])

    with tab2:
        st.subheader("Comprehensive Marketing Analysis Dashboard")
        
        with st.expander("Input Your Business Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                main_url = st.text_input("Your Website URL:", placeholder="https://example.com", key="comp_url")
                brand_name = st.text_input("Brand Name:", key="comp_brand")
            with col2:
                keywords = st.text_input("Target Keywords (comma-separated):", placeholder="e.g., keyword1, keyword2", key="comp_comp_keywords")
                industry = st.text_input("Industry:", key="comp_industry")

        with st.expander("Competitor Details"):
            num_competitors = st.number_input("Number of Competitors:", min_value=1, max_value=3, value=1, key="comp_num_comp")
            competitors = []
            for i in range(num_competitors):
                comp_url = st.text_input(f"Competitor {i+1} URL:", key=f"comp_comp_url_{i}")
                competitors.append(comp_url)

        st.markdown("### Analysis Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()

        if st.button("Generate Comprehensive Report", key="comp_button"):
            if not all([main_url, brand_name, industry]) or not all(competitors):
                st.error("Please fill in all required fields")
                return
            
            with st.spinner("Generating comprehensive marketing analysis..."):
                current_date = datetime(2025, 3, 24)
                keywords_list = [k.strip() for k in keywords.split(',')] if keywords else ["generic"]

                status_text.text("Step 1/4: Analyzing SEO...")
                seo_results = marketing_system.seo_optimizer(main_url, keywords_list)
                progress_bar.progress(0.25)

                status_text.text("Step 2/4: Analyzing competitors...")
                competitor_results = marketing_system.competitor_watchdog(competitors, keywords_list)
                progress_bar.progress(0.5)

                status_text.text("Step 3/4: Generating content ideas...")
                content_results = marketing_system.post_creator(f"{industry} trends", "LinkedIn", "professional")
                progress_bar.progress(0.75)

                status_text.text("Step 4/4: Creating email strategy...")
                audience = [
                    {"segment_name": "New Customers", "characteristics": "First-time Buyers", "engagement": "Medium"},
                    {"segment_name": "Returning Customers", "characteristics": "Repeat Customers", "engagement": "High"}
                ]
                email_results = marketing_system.smart_email_manager("Promotional", audience)
                progress_bar.progress(0.9)

                status_text.text("Compiling final report with deadlines...")
                competitor_str = ", ".join(competitors)
                summary_prompt = f"""
                Create a comprehensive marketing analysis report based on:
                Website: {main_url}
                Brand: {brand_name}
                Industry: {industry}
                Keywords: {', '.join(keywords_list)}
                Competitors: {competitor_str}
                SEO Analysis: {seo_results.get('recommendations', 'N/A')}
                Competitor Insights: {', '.join([f"{comp}: {data['analysis']}" for comp, data in competitor_results.items()])}
                Content Suggestions: {content_results['content']}
                Email Strategy: {', '.join([f"{seg}: {data['content'][:100]}..." for seg, data in email_results.items()])}
                
                Provide a detailed report with:
                1. Executive Summary
                2. Current Market Position
                3. Competitive Landscape
                4. Marketing Opportunities
                5. Action Plan with specific deadlines starting from {current_date.strftime('%Y-%m-%d')}:
                   - Short-term actions (within 1 week)
                   - Medium-term actions (within 1 month)
                   - Long-term actions (within 3 months)
                """
                comprehensive_report = marketing_system._get_completion(summary_prompt)
                progress_bar.progress(1.0)

                st.markdown("---")
                st.subheader("Comprehensive Marketing Analysis Report")
                
                # Full report section first
                with st.expander("Full Report", expanded=True):
                    st.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Brand:** {brand_name}")
                    st.markdown(comprehensive_report)

                st.markdown("### Action Plan Timeline")
                deadlines = {
                    "Short-term (1 week)": current_date + timedelta(weeks=1),
                    "Medium-term (1 month)": current_date + timedelta(weeks=4),
                    "Long-term (3 months)": current_date + timedelta(weeks=12)
                }
                for term, deadline in deadlines.items():
                    st.write(f"**{term}:** {deadline.strftime('%Y-%m-%d')}")

                # Key Findings Summary moved after full report
                st.markdown("### Key Findings Summary")
                summary_data = {
                    "Aspect": ["Website", "Industry", "Keywords", "Competitors"],
                    "Details": [main_url, industry, ", ".join(keywords_list), competitor_str]
                }
                st.table(summary_data)

                # Competitive Landscape Analysis section with scores
                st.markdown("### Competitive Analysis & Scoring")

                # Display detailed analysis for each competitor
                for competitor, data in competitor_results.items():
                    st.markdown(f'<div class="competitor-card">', unsafe_allow_html=True)
                    st.subheader(f"Analysis for {competitor}")
                    
                    # Display metrics in a grid
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Key Metrics")
                        st.markdown(f'<div class="metric-box">{data["metrics"]}</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("### Quick Summary")
                        st.markdown(f'<div class="metric-box">{data["quick_summary"]}</div>', unsafe_allow_html=True)
                    
                    # Parse and display analysis sections
                    analysis_text = data['analysis']
                    sections = {
                        "Content Strategy": "",
                        "Keyword Analysis": "",
                        "Market Presence": "",
                        "Competitive Advantages": "",
                        "Actionable Recommendations": ""
                    }
                    
                    # Parse sections
                    current_section = ""
                    current_content = []
                    
                    for line in analysis_text.split('\n'):
                        if any(section in line for section in sections.keys()):
                            if current_section and current_content:
                                sections[current_section] = '\n'.join(current_content)
                                current_content = []
                            current_section = next(section for section in sections.keys() if section in line)
                        elif current_section and line.strip():
                            current_content.append(line)
                    
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Display sections in tabs
                    analysis_tabs = st.tabs(list(sections.keys()))
                    
                    for tab, (section_name, content) in zip(analysis_tabs, sections.items()):
                        with tab:
                            if content:
                                st.markdown(content)
                            else:
                                st.markdown("*Analysis for this section is being generated...*")
                    
                    st.markdown("---")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.download_button(
                    label="Download Report",
                    data=comprehensive_report,
                    file_name=f"{brand_name}_marketing_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
                status_text.text("Report complete!")

if __name__ == "__main__":
    main()