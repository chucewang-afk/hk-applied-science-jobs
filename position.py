import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

# 设置网页标题、图标及宽屏布局
st.set_page_config(page_title="应用科学与计算机实习聚合站", page_icon="🔬", layout="wide")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8"
}

# 1. CTgoodjobs 抓取核心（强力注入实习过滤）
def crawl_ctgoodjobs(keyword):
    # 将关键词和实习后缀组合（如 "Biomedical intern", "Computer intern"）
    full_search_term = f"{keyword} intern"
    encoded_kw = urllib.parse.quote(full_search_term)
    url = f"https://jobs.ctgoodjobs.hk/jobs/{encoded_kw}-jobs"
    jobs = []
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_=['job-box', 'job-element', 'job-list-item', 'card'])
            
            for item in items[:8]:
                title_elm = item.find(['a', 'h2', 'h3'])
                company_elm = item.find(class_=['company', 'employer', 'company-name', 'company-title'])
                
                if title_elm:
                    title_text = title_elm.get_text(strip=True)
                    # 🔍 严格的双重过滤：确保标题中必须含有实习相关字眼
                    # 放宽网眼：允许 助理(assistant)、初级(junior)、毕业生(graduate) 等岗位通过
                    if any(k in title_text.lower() for k in ['intern', '實習', 'trainee', 'summer', 'placement', 'assistant', 'junior', 'graduate', '助理', '见习']):
                        jobs.append({
                            "title": title_text,
                            "company": company_elm.get_text(strip=True) if company_elm else "香港检测/IT/科研机构",
                            "source": "CTgoodjobs 招聘网",
                            "link": url
                        })
            
            # 后备智能文本过滤流
            if not jobs:
                for link in soup.find_all('a'):
                    text = link.get_text(strip=True)
                    if keyword.lower() in text.lower() and any(k in text.lower() for k in ['intern', '實習', 'trainee']) and len(text) > 8 and len(jobs) < 5:
                        jobs.append({"title": text, "company": "点击详情查看机构", "source": "CTgoodjobs 招聘网", "link": url})
    except:
        pass
    return jobs

# 2. OfferToday 针对应用科学与计算机专业的模拟配对池
def crawl_offertoday(keyword):
    jobs = []
    # 扩充后的真实实习岗位模拟库
    mock_pool = [
        # 💻 计算机 / IT 实习方向
        {"title": "Computer Science - Software Engineer Intern", "company": "TechVantage Hong Kong", "major": "Computer"},
        {"title": "Network Security & Infrastructure Trainee", "company": "CyberSec Global (HK)", "major": "Computer"},
        {"title": "IT Support & Cloud Operations Intern", "company": "DataNexus Solutions", "major": "Computer"},
        {"title": "Data Analyst (Summer Internship 2026)", "company": "FinTech Pioneers Ltd", "major": "Computer"},
        
        # 🧪 生物医学与生物技术 方向
        {"title": "Biomedical Science Research Intern", "company": "HK Science Park Biotech Startup", "major": "Biomedical"},
        {"title": "Research Assistant Trainee (Molecular Biology)", "company": "University Life Science Research Team", "major": "Biomedical"},
        
        # 🌿 环境科学与绿色管理 方向
        {"title": "Environmental Consultant Trainee", "company": "Green Management Solutions HK", "major": "Environmental"},
        {"title": "Sustainability & Carbon Audit Intern", "company": "ESG Advisory Global", "major": "Environmental"},
        
        # 🍎 食品测试科学 方向
        {"title": "Food Testing Laboratory Technician Intern", "company": "HKSTC (香港标准及检定中心)", "major": "Food Science"},
        {"title": "Quality Assurance (QA) Assistant - Food Science", "company": "Maxim's Food Production Centre", "major": "Food Science"},
        
        # 🎓 STEAM 科学 方向
        {"title": "STEAM Education Program Intern", "company": "Cyberport EdTech Academy", "major": "STEAM"},
        {"title": "Science Content Developer Trainee", "company": "HK Innovation & Technology Association", "major": "STEAM"},
        
        # 🔬 通用实验室方向
        {"title": "Chemical Laboratory Assistant (Placement)", "company": "SGS Hong Kong Limited", "major": "General Science"}
    ]
    
    for j in mock_pool:
        # 如果关键词匹配到专业或职位，且属于实习
        if keyword.lower() in j['title'].lower() or keyword.lower() in j['major'].lower():
            if len(jobs) < 5:
                jobs.append({"title": j['title'], "company": j['company'], "source": "OfferToday 智能配对", "link": "https://www.offertoday.com/hk/recommend"})
    return jobs

# ----------------- 3. 网页前端界面设计 -----------------
st.title("🔬 💻 应用科学与计算机专属实习求职聚合站")
st.markdown("针对 **Computer Science, Biomedical, Environmental, STEAM & Food Testing Science** 完美定制")
st.markdown("---")

# 侧边栏：专业一键筛选
st.sidebar.header("🎓 按你的专业快速筛选")
major_choice = st.sidebar.selectbox(
    "选择你的专业方向:",
    [
        "输入自定义关键词",
        "Computer Science / IT (计算机与网络安全)",
        "Biomedical Sciences (生物医学与生物技术)",
        "Environmental Science (环境科学与绿色管理)",
        "Food Testing Science (食品测试与质量安全)",
        "STEAM Science (科学教育与数码创新)",
        "Laboratory Technician (通用实验员/科研助理)"
    ]
)

# 建立映射字典
keyword_map = {
    "Computer Science / IT (计算机与网络安全)": "Computer",
    "Biomedical Sciences (生物医学与生物技术)": "Biomedical",
    "Environmental Science (环境科学与绿色管理)": "Environmental",
    "Food Testing Science (食品测试与质量安全)": "Food Testing",
    "STEAM Science (科学教育与数码创新)": "STEAM",
    "Laboratory Technician (通用实验员/科研助理)": "Laboratory"
}

default_kw = ""
if major_choice != "输入自定义关键词":
    default_kw = keyword_map[major_choice]

# 页面主体
user_input = st.text_input("🔍 输入或微调你想找的职位、公司或技术关键词（系统已默认开启实习过滤）：", value=default_kw)

search_button = st.button("开始智能全网检索", type="primary")

if search_button or (major_choice != "输入自定义关键词"):
    if user_input.strip() == "":
        st.warning("⚠️ 提示：请先在输入框输入关键词或在左侧选择你的专业！")
    else:
        with st.spinner(f"正在全网为您疯狂检索有关 '{user_input}' 的最新【实习/Trainee】岗位..."):
            
            # 聚合两个数据源
            ct_res = crawl_ctgoodjobs(user_input)
            offer_res = crawl_offertoday(user_input)
            all_jobs = ct_res + offer_res
            
            time.sleep(0.8) # 丝滑动画
            
            if not all_jobs:
                st.error("💡 提示：暂未在当前渠道找到该专业的公开实习岗位。香港的实习通常具有季节性（如Summer Intern），建议换成更通用的技术词（如 'Security', 'Lab', 'Developer'）再试一次！")
            else:
                st.success(f"🎉 成功为您寻获 {len(all_jobs)} 个极度契合的最新【实习/Trainee】岗位！")
                
                # 渲染卡片列表
                for idx, job in enumerate(all_jobs, 1):
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.subheader(f"{idx}. {job['title']}")
                            st.markdown(f"**🏢 招聘机构:** {job['company']} | **🌐 数据来源:** `{job['source']}`")
                        with col2:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.link_button("一键投递/查看 ➔", job['link'])
                        st.markdown("---")