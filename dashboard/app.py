"""
SQL Guardian - Web Dashboard
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.static_analyzer.analyzer import StaticAnalyzer

# Page config
st.set_page_config(
    page_title="SQL Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .critical { color: #d32f2f; }
    .warning { color: #f57c00; }
    .info { color: #1976d2; }
    .success { color: #388e3c; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🛡️ SQL Guardian</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">AI-Powered SQL Code Analysis Tool</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    use_ai = st.checkbox("Use AI Explanations", value=True, 
                         help="Enable AI-powered explanations (slower but more detailed)")
    
    st.markdown("---")
    st.markdown("### 📊 About")
    st.info("""
    **SQL Guardian** analyzes your T-SQL code for:
    - Performance issues
    - Best practices
    - Security concerns
    - Code quality
    """)
    
    st.markdown("### 🔍 Rules Active")
    st.write("✓ SELECT * detection")
    st.write("✓ Non-sargable predicates")
    st.write("✓ Cursor usage")
    st.write("✓ NOLOCK hint")
    st.write("✓ SET NOCOUNT ON")

# Main content
tab1, tab2, tab3 = st.tabs(["📝 Analyze Code", "📁 Analyze File", "📈 About"])

with tab1:
    st.header("Paste SQL Code")
    
    # Sample code
    default_code = """CREATE PROCEDURE usp_GetOrders
AS
BEGIN
    SELECT * 
    FROM Orders 
    WHERE YEAR(OrderDate) = 2026
END"""
    
    sql_code = st.text_area(
        "SQL Code:",
        value=default_code,
        height=300,
        help="Paste your T-SQL code here"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        analyze_btn = st.button("🔍 Analyze Code", type="primary", use_container_width=True)
    
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_btn:
        st.rerun()
    
    if analyze_btn and sql_code.strip():
        with st.spinner("🤖 Analyzing your SQL code..."):
            analyzer = StaticAnalyzer(use_ai=use_ai)
            result = analyzer.analyze_code(sql_code, "pasted_code")
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Issues", result['total_violations'])
        
        with col2:
            st.metric("Critical", result['critical'], 
                     delta=None if result['critical'] == 0 else "Action Required",
                     delta_color="inverse")
        
        with col3:
            st.metric("Warnings", result['warnings'],
                     delta=None if result['warnings'] == 0 else "Review Needed",
                     delta_color="inverse")
        
        with col4:
            st.metric("Info", result['info'],
                     delta=None if result['info'] == 0 else "Suggestions",
                     delta_color="off")
        
        # Show violations
        if result['violations']:
            st.markdown("### 🔍 Issues Found")
            
            for i, violation in enumerate(result['violations'], 1):
                severity_colors = {
                    'CRITICAL': '🔴',
                    'WARNING': '⚠️',
                    'INFO': 'ℹ️'
                }
                
                severity_class = {
                    'CRITICAL': 'critical',
                    'WARNING': 'warning',
                    'INFO': 'info'
                }
                
                emoji = severity_colors.get(violation['severity'], '•')
                color_class = severity_class.get(violation['severity'], 'info')
                
                with st.expander(f"{emoji} Issue #{i}: [{violation['severity']}] {violation['rule_id']} - {violation['message']}", expanded=True):
                    st.markdown(f"**Line:** {violation['line']}")
                    
                    st.markdown("**Code Context:**")
                    st.code(violation['code_snippet'], language='sql')
                    
                    if 'ai_explanation' in violation and use_ai:
                        st.markdown("**🤖 AI Analysis:**")
                        st.info(violation['ai_explanation'])
        else:
            st.success("✅ No issues found! Your SQL code looks great!")
            st.balloons()

with tab2:
    st.header("Upload SQL File")
    
    uploaded_file = st.file_uploader(
        "Choose a SQL file",
        type=['sql'],
        help="Upload a .sql file to analyze"
    )
    
    if uploaded_file is not None:
        # Read file
        sql_content = uploaded_file.read().decode('utf-8')
        
        st.markdown("### 📄 File Content Preview")
        with st.expander("View file content", expanded=False):
            st.code(sql_content, language='sql')
        
        if st.button("🔍 Analyze File", type="primary"):
            with st.spinner(f"🤖 Analyzing {uploaded_file.name}..."):
                analyzer = StaticAnalyzer(use_ai=use_ai)
                result = analyzer.analyze_code(sql_content, uploaded_file.name)
            
            # Display results (same as tab1)
            st.markdown("---")
            st.subheader("📊 Analysis Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Issues", result['total_violations'])
            with col2:
                st.metric("Critical", result['critical'])
            with col3:
                st.metric("Warnings", result['warnings'])
            with col4:
                st.metric("Info", result['info'])
            
            if result['violations']:
                st.markdown("### 🔍 Issues Found")
                
                for i, violation in enumerate(result['violations'], 1):
                    emoji = {'CRITICAL': '🔴', 'WARNING': '⚠️', 'INFO': 'ℹ️'}.get(violation['severity'], '•')
                    
                    with st.expander(f"{emoji} Issue #{i}: [{violation['severity']}] {violation['rule_id']} - {violation['message']}", expanded=False):
                        st.markdown(f"**Line:** {violation['line']}")
                        st.markdown("**Code Context:**")
                        st.code(violation['code_snippet'], language='sql')
                        
                        if 'ai_explanation' in violation and use_ai:
                            st.markdown("**🤖 AI Analysis:**")
                            st.info(violation['ai_explanation'])
            else:
                st.success("✅ No issues found!")
                st.balloons()

with tab3:
    st.header("About SQL Guardian")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 What It Does
        
        SQL Guardian is a **free, AI-powered** static code analyzer for T-SQL that helps you:
        
        - **Catch performance issues** before deployment
        - **Enforce best practices** across your team
        - **Identify security concerns** in SQL code
        - **Learn from AI explanations** for each issue
        
        ### 🚀 Features
        
        - ✅ 5+ built-in rules
        - ✅ Local AI (Ollama) - No API costs
        - ✅ Detailed explanations
        - ✅ Web interface + CLI tool
        - ✅ 100% free and open source
        """)
    
    with col2:
        st.markdown("""
        ### 📋 Rules Detected
        
        1. **SELECT * Usage** (WARNING)
           - Recommends explicit column selection
        
        2. **Non-Sargable Predicates** (WARNING)
           - Functions in WHERE clause
        
        3. **Cursor Usage** (WARNING)
           - Suggests set-based alternatives
        
        4. **NOLOCK Hint** (WARNING)
           - Warns about dirty reads
        
        5. **Missing SET NOCOUNT ON** (INFO)
           - Best practice for stored procedures
        
        ### 💰 Cost
        
        **$0** - Completely free!
        - No API costs
        - Runs locally
        - Open source
        """)
    
    st.markdown("---")
    st.markdown("### 🛠️ Tech Stack")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Python** - Core language")
    with col2:
        st.info("**Ollama** - Local AI (DeepSeek-Coder)")
    with col3:
        st.info("**Streamlit** - Web dashboard")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666;">SQL Guardian v1.0 | Built with ❤️ for Database Engineers</p>',
    unsafe_allow_html=True
)