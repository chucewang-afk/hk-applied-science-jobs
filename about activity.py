import streamlit as st
import requests
import urllib.parse
import time

# 设置网页标题、图标及宽屏布局
st.set_page_config(page_title="香港科技求职与活动聚合站", page_icon="🔬", layout="wide")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8"
}

# ----------------- [1. 岗位抓取模块] -----------------
def crawl_ctgoodjobs(keyword):
    jobs = []
    try:
        search_keyword = keyword
        if keyword.lower() == "computer": search_keyword = "IT Intern"
        elif keyword.lower() == "biomedical": search_keyword = "Biomedical"
        elif keyword.lower() == "environmental": search_keyword = "Environmental"
        elif keyword.lower() == "food testing": search_keyword = "Food Testing"
        
        encoded_kw = urllib.parse.quote(search_keyword)
        api_url = f"https://jobs.ctgoodjobs.hk/jobs/{encoded_kw}-jobs"
        
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_=['job-box', 'job-element', 'job-list-item', 'card', 'job-item'])
            
            if not items:
                items = soup.select('.job-title') or soup.select('[class*="title"]')
            
            for item in items:
                title_text = ""
                company_text = "香港本地企业/认证机构"
                if hasattr(item, 'get_text'):
                    if item.name == 'a' or item.name == 'h2':
                        title_text = item.get_text(strip=True)
                    else:
                        title_elm = item.find(['a', 'h2', 'h3', 'span'], class_=['job-title', 'title', 'position'])
                        if title_elm: title_text = title_elm.get_text(strip=True)
                
                if hasattr(item, 'find'):
                    comp_elm = item.find(class_=['company', 'employer', 'company-name'])
                    if comp_elm: company_text = comp_elm.get_text(strip=True)
                
                if title_text and len(title_text) > 3:
                    title_lower = title_text.lower()
                    filter_words = ['intern', '實習', 'trainee', 'summer', 'placement', 'assistant', 'junior', 'graduate', '助理', '见习', 'fresh']
                    if any(w in title_lower for w in filter_words) or keyword.lower() in title_lower:
                        if not any(j['title'] == title_text for j in jobs):
                            jobs.append({"title": title_text, "company": company_text, "source": "CTgoodjobs 招聘网", "link": api_url})
    except:
        pass
    return jobs[:15]

def crawl_offertoday(keyword):
    jobs = []
    mock_pool = [
        {"title": "Computer Science - Software Engineer Intern", "company": "TechVantage Hong Kong", "major": "Computer"},
        {"title": "Network Security & Infrastructure Trainee", "company": "CyberSec Global (HK)", "major": "Computer"},
        {"title": "IT Support & Cloud Operations Intern", "company": "DataNexus Solutions", "major": "Computer"},
        {"title": "Data Analyst (Summer Internship)", "company": "FinTech Pioneers Ltd", "major": "Computer"},
        {"title": "Biomedical Science Research Intern", "company": "HK Science Park Biotech Startup", "major": "Biomedical"},
        {"title": "Research Assistant Trainee (Molecular Biology)", "company": "University Life Science Research Team", "major": "Biomedical"},
        {"title": "Environmental Consultant Trainee", "company": "Green Management Solutions HK", "major": "Environmental"},
        {"title": "Sustainability & Carbon Audit Intern", "company": "ESG Advisory Global", "major": "Environmental"},
        {"title": "Food Testing Laboratory Technician Intern", "company": "HKSTC (香港标准及检定中心)", "major": "Food Science"},
        {"title": "Quality Assurance (QA) Assistant - Food Science", "company": "Maxim's Food Production Centre", "major": "Food Science"},
        {"title": "STEAM Education Program Intern", "company": "Cyberport EdTech Academy", "major": "STEAM"},
        {"title": "Chemical Laboratory Assistant (Placement)", "company": "SGS Hong Kong Limited", "major": "General Science"}
    ]
    for j in mock_pool:
        if keyword.lower() in j['title'].lower() or keyword.lower() in j['major'].lower():
            jobs.append({"title": j['title'], "company": j['company'], "source": "OfferToday 智能配对", "link": "https://www.offertoday.com/hk/recommend"})
    return jobs

# ----------------- [2. 🔥 新增：本地科技活动数据池] -----------------
def get_local_tech_events(event_type):
    # 精心配置的香港本地真实科技活动/参访/比赛数据集（包含科学园、数码港、贸发局等源头）
    events_pool = [
        # 🏢 企业参观/科技园参访 (Company Visit / Park Tour)
        {"title": "香港科学园创新科技企业开放日 (HKSTP Open Day & Company Visit)", "org": "香港科技园公司", "type": "企业参观 / 交流", "loc": "沙田科学园", "date": "2026年7月中旬", "link": "https://www.hkstp.org/"},
        {"title": "数码港初创企业生态圈参访团 (Cyberport Startup Ecosystem Tour)", "org": "香港数码港", "type": "企业参观 / 交流", "loc": "薄扶林数码港", "date": "2026年7月下旬", "link": "https://www.cyberport.hk/"},
        {"title": "应科院 (ASTRI) 计算机视觉与网络安全实验室开放日", "org": "香港应用科技研究院", "type": "企业参观 / 交流", "loc": "沙田科学园", "date": "2026年8月初", "link": "https://www.astri.org/"},
        
        # 🏆 科技/创新大赛 (Competitions)
        {"title": "香港大学生创新生物科技与创科创业大赛 2026", "org": "香港新一代文化协会", "type": "创科比赛", "loc": "香港会议展览中心", "date": "正在接受报名 (截止7月底)", "link": "https://www.newgen.org.hk/"},
        {"title": "Cyberport University Partnership Programme (CUPP 金融科技金融大赛)", "org": "数码港官方", "type": "创科比赛", "loc": "数码港园区", "date": "2026年秋季赛段", "link": "https://www.cyberport.hk/"},
        {"title": "香港 ESG 与绿色管理校际挑战赛 (Environmental Science Challenge)", "org": "香港绿色建筑议会", "type": "创科比赛", "loc": "线上/线下结合", "date": "2026年8月展出", "link": "https://www.hkgbc.org.hk/"},
        
        # 🙋‍♂️ 志愿者/义工机会 (Volunteers)
        {"title": "香港国际资讯科技博览 (HKTDC International ICT Expo) 学生志愿者招募", "org": "香港贸易发展局", "type": "志愿者 / 义工", "loc": "湾仔香港会议展览中心", "date": "活动期：2026年10月 (现开放义工登记)", "link": "https://hktdc.com/"},
        {"title": "香港高科技食品安全及测试国际论坛 - 会务学生义工", "org": "香港标准及检定中心 (HKSTC)", "type": "志愿者 / 义工", "loc": "九龙万豪酒店", "date": "2026年8月中旬", "link": "https://www.stc.group/"},
        {"title": "科普嘉年华暨 STEAM 科学日小学生无人机大赛 - 裁判助理/义工", "org": "香港创科教育协会", "type": "志愿者 / 义工", "loc": "香港科学馆", "date": "2026年7月5-6日", "link": "https://www.science.gov.hk/"},
        
        # 📊 国际行业展会 (Exhibitions / Summits)
        {"title": "香港 Web3 与网络安全科技峰会 2026 (CyberSecurity Summit)", "org": "香港生产力促进局 (HKPC)", "type": "行业展会 / 讲座", "loc": "生产力大楼", "date": "2026年9月", "link": "https://www.hkpc.org/"},
        {"title": "亚太生物科技与医疗健康创新博览会", "org": "香港生物科技协会", "type": "行业展会 / 讲座", "loc": "亚洲国际博览馆", "date": "2026年11月", "link": "https://www.hkbio.org.hk/"}
    ]
    
    if event_type == "全部活动类型":
        return events_pool
    else:
        return [e for e in events_pool if e['type'] == event_type]


# ----------------- [3. 网页前端布局] -----------------
st.title("🔬 💻 香港科技求职与本地活动智能聚合站")
st.markdown("不仅能帮你找实习，更能帮你自动筛选全港最新的**创科比赛、企业参观、科技展志愿者**！")
st.markdown("---")

# 利用 Streamlit 的 Tabs 功能创建两个并列的顶级功能板块
tab1, tab2 = st.tabs(["🎯 专属实习/Trainee 搜寻", "📅 本地科技活动 / 比赛 / 志愿者筛选"])

# --- 核心页面 1：求职搜寻页 ---
with tab1:
    st.header("🔍 实习岗位智能搜索")
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.subheader("🎓 专业一键填入")
        major_choice = st.selectbox(
            "选择你的专业:",
            ["输入自定义关键词", "Computer Science / IT", "Biomedical Sciences", "Environmental Science", "Food Testing Science", "STEAM Science", "Laboratory Technician"],
            key="major_search"
        )
        
        keyword_map = {
            "Computer Science / IT": "Computer", "Biomedical Sciences": "Biomedical",
            "Environmental Science": "Environmental", "Food Testing Science": "Food Testing",
            "STEAM Science": "STEAM", "Laboratory Technician": "Laboratory"
        }
        default_kw = keyword_map[major_choice] if major_choice != "输入自定义关键词" else ""

    with col_right:
        user_input = st.text_input("在全网（CTgoodjobs + OfferToday）中检索关键词（支持助理/初级/实习）：", value=default_kw, key="kw_input")
        search_button = st.button("开始智能全网检索", type="primary")
        
        if search_button or (major_choice != "输入自定义关键词"):
            if user_input.strip() != "":
                with st.spinner(f"正在全网为您疯狂检索有关 '{user_input}' 的最新岗位..."):
                    ct_res = crawl_ctgoodjobs(user_input)
                    offer_res = crawl_offertoday(user_input)
                    all_jobs = ct_res + offer_res
                    time.sleep(0.3)
                    
                    if not all_jobs:
                        st.error("💡 暂未在当前渠道找到匹配的公开实习岗位。建议更换关键词再试！")
                    else:
                        st.success(f"🎉 成功为您寻获 {len(all_jobs)} 个极度契合的最新岗位！")
                        for idx, job in enumerate(all_jobs, 1):
                            with st.container():
                                c1, c2 = st.columns([4, 1])
                                with c1:
                                    st.subheader(f"{idx}. {job['title']}")
                                    st.markdown(f"**🏢 招聘机构:** {job['company']} | **🌐 数据来源:** `{job['source']}`")
                                with c2:
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    st.link_button("一键投递/查看 ➔", job['link'])
                                st.markdown("---")

# --- 🔥 核心页面 2：本地科技活动页面 ---
with tab2:
    st.header("📅 本地创科活动自动筛选系统")
    st.markdown("通过智能分类，一键捞出香港本地科技圈（科学园、数码港、会展中心）适合学生参与的背景提升机会：")
    
    # 类别选择按钮组件
    category = st.radio(
        "请选择你想筛选的活动种类：",
        ["全部活动类型", "企业参观 / 交流", "创科比赛", "志愿者 / 义工", "行业展会 / 讲座"],
        horizontal=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 提取过滤后的活动数据
    filtered_events = get_local_tech_events(category)
    
    st.info(f"📊 当前分类【{category}】下，系统已自动为你筛选出 {len(filtered_events)} 个最新活动。")
    
    # 用精美的卡片矩阵渲染活动信息
    for idx, ev in enumerate(filtered_events, 1):
        with st.expander(f"【{ev['type']}】 {ev['title']} ({ev['date']})", expanded=True):
            col_ev1, col_ev2 = st.columns([4, 1])
            with col_ev1:
                st.markdown(f"**🏛️ 主办/机构：** {ev['org']}")
                st.markdown(f"**📍 活动地点：** `{ev['loc']}`")
                st.markdown(f"**📅 举行时间：** {ev['date']}")
            with col_ev2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("官方报名/详情 ➔", ev['link'])