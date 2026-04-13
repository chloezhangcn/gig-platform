"""
校园星零工平台 - Streamlit MVP版本
功能：任务大厅、任务领取、作品提交、收益查看、管理员审核打分
"""
import streamlit as st
import json
import os
from datetime import datetime
import uuid

# ========== 数据存储 ==========
DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(filepath, default):
    ensure_data_dir()
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_json(filepath, data):
    ensure_data_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== 数据操作 ==========
def get_tasks():
    return load_json(TASKS_FILE, [])

def save_tasks(tasks):
    save_json(TASKS_FILE, tasks)

def get_submissions():
    return load_json(SUBMISSIONS_FILE, [])

def save_submissions(submissions):
    save_json(SUBMISSIONS_FILE, submissions)

def get_users():
    return load_json(USERS_FILE, {"merchants": [], "students": []})

def save_users(users):
    save_json(USERS_FILE, users)

# ========== 评分相关函数 ==========
def calculate_grade(score):
    """根据分数计算等级"""
    if score <= 40:
        return "不合格"
    elif score <= 60:
        return "合格"
    elif score <= 80:
        return "良好"
    else:
        return "优秀"

def calculate_coefficient(score):
    """根据分数计算结算系数"""
    if score <= 40:
        return 0.0  # 不合格
    elif score <= 60:
        return 0.8  # 合格
    elif score <= 80:
        return 1.0  # 良好
    else:
        return 1.2  # 优秀

def get_grade_emoji(grade):
    """获取等级对应的emoji"""
    emojis = {
        "不合格": "❌",
        "合格": "✅",
        "良好": "⭐",
        "优秀": "🏆"
    }
    return emojis.get(grade, "")

# ========== 页面配置 ==========
st.set_page_config(
    page_title="校园星零工平台",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
    }
    .task-card {
        padding: 15px;
        border-radius: 10px;
        background: #f0f2f6;
        margin: 10px 0;
    }
    .metric-card {
        text-align: center;
        padding: 20px;
        background: #e8f4fd;
        border-radius: 10px;
    }
    .score-excellent {background-color: #d4edda; padding: 10px; border-radius: 8px; border-left: 4px solid #28a745;}
    .score-good {background-color: #cce5ff; padding: 10px; border-radius: 8px; border-left: 4px solid #007bff;}
    .score-pass {background-color: #fff3cd; padding: 10px; border-radius: 8px; border-left: 4px solid #ffc107;}
    .score-fail {background-color: #f8d7da; padding: 10px; border-radius: 8px; border-left: 4px solid #dc3545;}
    .grade-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        color: white;
    }
    .grade-excellent {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .grade-good {background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);}
    .grade-pass {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);}
    .grade-fail {background: linear-gradient(135deg, #434343 0%, #000000 100%);}
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏：角色选择 ==========
st.sidebar.title("🎬 校园星零工平台")

role = st.sidebar.radio(
    "请选择你的角色：",
    ["👨‍🎓 我是学生", "🏢 我是商家（大区）", "👨‍💼 我是管理员"]
)

# ========== 页面：学生端 ==========
if role == "👨‍🎓 我是学生":
    st.title("👨‍🎓 学生端 - 任务大厅")
    
    # 登录/注册
    with st.expander("👤 个人信息", expanded=True):
        student_name = st.text_input("请输入你的姓名", key="student_login")
        student_phone = st.text_input("请输入你的手机号", key="student_phone")
        student_school = st.selectbox("请选择你的学校", 
            ["浙江大学", "北京大学", "中西部高校", "其他"])
    
    if not student_name:
        st.info("👆 请先填写姓名和手机号，然后开始接单！")
        st.stop()
    
    # 任务大厅
    st.divider()
    st.subheader("📋 任务大厅")
    
    tasks = get_tasks()
    available_tasks = [t for t in tasks if t.get("status") == "open"]
    
    # 筛选
    filter_region = st.selectbox("筛选大区", ["全部", "北大区", "浙大区", "中西部"])
    filter_type = st.selectbox("筛选类型", ["全部", "短视频拍摄", "脚本撰写", "账号代运营", "直播助播"])
    
    filtered_tasks = available_tasks
    if filter_region != "全部":
        filtered_tasks = [t for t in filtered_tasks if t.get("region") == filter_region]
    if filter_type != "全部":
        filtered_tasks = [t for t in filtered_tasks if t.get("task_type") == filter_type]
    
    st.markdown(f"**共 {len(filtered_tasks)} 个任务可接**")
    
    # 展示任务卡片
    for task in filtered_tasks:
        with st.container():
            st.markdown(f"""
            <div class="task-card">
                <h4>{task['title']}</h4>
                <p><b>单价：</b>💰 {task['price']}元/条</p>
                <p><b>剩余：</b>{task['remaining']}/{task['total']}个</p>
                <p><b>要求：</b>{task['requirements'][:50]}...</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"🎯 领取任务", key=f"take_{task['id']}"):
                    # 检查是否已领取
                    submissions = get_submissions()
                    already_taken = any(
                        s["student_phone"] == student_phone and s["task_id"] == task["id"] 
                        for s in submissions
                    )
                    if already_taken:
                        st.error("❌ 你已经领取过这个任务了！")
                    else:
                        # 创建新提交
                        new_submission = {
                            "id": str(uuid.uuid4()),
                            "task_id": task["id"],
                            "task_title": task["title"],
                            "task_price": task["price"],  # 保存任务单价
                            "student_name": student_name,
                            "student_phone": student_phone,
                            "student_school": student_school,
                            "status": "pending",
                            "video_url": "",
                            "notes": "",
                            "score": None,  # 评分分数
                            "grade": None,  # 等级
                            "coefficient": None,  # 结算系数
                            "amount": None,  # 结算金额
                            "reviewed_by": None,  # 审核人
                            "reviewed_at": None,  # 审核时间
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        submissions.append(new_submission)
                        save_submissions(submissions)
                        
                        # 更新任务剩余数量
                        task["remaining"] -= 1
                        if task["remaining"] <= 0:
                            task["status"] = "full"
                        save_tasks(tasks)
                        
                        st.success("✅ 任务领取成功！请尽快完成并提交作品")
            with col2:
                st.button(f"📋 查看详情", key=f"view_{task['id']}")
    
    # 我的任务
    st.divider()
    st.subheader("📂 我的任务")
    
    submissions = get_submissions()
    my_tasks = [s for s in submissions if s["student_phone"] == student_phone]
    
    if not my_tasks:
        st.info("你还没有领取任何任务，快去任务大厅看看吧！")
    else:
        for my_task in my_tasks:
            with st.expander(f"📌 {my_task['task_title']} - {my_task['status']}"):
                st.write(f"**任务ID：**{my_task['task_id']}")
                st.write(f"**领取时间：**{my_task['created_at']}")
                
                # 状态颜色
                status_emoji = {"pending": "⏳", "submitted": "📤", "approved": "✅", "rejected": "❌"}
                st.write(f"**状态：**{status_emoji.get(my_task['status'], '')} {my_task['status']}")
                
                # 显示评分信息（如果有）
                if my_task.get("score") is not None:
                    grade = my_task.get("grade", "")
                    grade_emoji = get_grade_emoji(grade)
                    st.write(f"**评分：**{my_task['score']}分 {grade_emoji} {grade}")
                    st.write(f"**结算系数：**{my_task.get('coefficient', 0)}")
                    if my_task.get("amount"):
                        st.write(f"**结算金额：**💰 {my_task['amount']} 元")
                
                # 提交作品
                if my_task["status"] == "pending":
                    video_url = st.text_input("请输入视频链接（抖音/视频号/B站）", key=f"url_{my_task['id']}")
                    notes = st.text_area("备注说明", key=f"notes_{my_task['id']}")
                    
                    if st.button("📤 提交作品", key=f"submit_{my_task['id']}"):
                        if not video_url:
                            st.error("请填写视频链接！")
                        else:
                            # 更新提交
                            for s in submissions:
                                if s["id"] == my_task["id"]:
                                    s["video_url"] = video_url
                                    s["notes"] = notes
                                    s["status"] = "submitted"
                                    s["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            save_submissions(submissions)
                            st.success("✅ 作品已提交，等待商家审核！")
                            st.rerun()
                
                if my_task.get("video_url"):
                    st.write(f"**视频链接：**{my_task['video_url']}")
                if my_task.get("notes"):
                    st.write(f"**备注：**{my_task['notes']}")
                if my_task.get("reviewed_at"):
                    st.write(f"**审核时间：**{my_task['reviewed_at']}")
    
    # 我的收益
    st.divider()
    st.subheader("💰 我的收益")
    
    approved_tasks = [s for s in my_tasks if s["status"] == "approved"]
    total_earnings = sum(s.get("amount", 0) for s in approved_tasks)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("已完成任务", len(approved_tasks))
    with col2:
        st.metric("待审核", len([s for s in my_tasks if s["status"] == "submitted"]))
    with col3:
        st.metric("总收入", f"¥{total_earnings}")

# ========== 页面：商家端 ==========
elif role == "🏢 我是商家（大区）":
    st.title("🏢 商家端 - 任务管理")
    
    # 登录
    with st.expander("🏢 商家信息", expanded=True):
        merchant_name = st.text_input("请输入大区/商家名称", key="merchant_login")
        merchant_region = st.selectbox("选择大区", ["北大区", "浙大区", "中西部"])
    
    if not merchant_name:
        st.info("👆 请先填写商家名称")
        st.stop()
    
    # 功能选择
    tab1, tab2 = st.tabs(["📝 发布任务", "📋 审核作品"])
    
    with tab1:
        st.subheader("📝 发布新任务")
        
        with st.form("new_task_form"):
            task_title = st.text_input("任务标题", placeholder="如：抖音短视频拍摄-阿里国际站产品种草")
            task_type = st.selectbox("任务类型", ["短视频拍摄", "脚本撰写", "账号代运营", "直播助播"])
            task_desc = st.text_area("任务描述/要求", placeholder="描述具体要求...")
            task_price = st.number_input("单价（元/条）", min_value=10, max_value=1000, value=50)
            task_total = st.number_input("任务总量", min_value=1, max_value=1000, value=10)
            
            submitted = st.form_submit_button("🚀 发布任务")
            
            if submitted:
                if not task_title or not task_desc:
                    st.error("请填写完整信息")
                else:
                    tasks = get_tasks()
                    new_task = {
                        "id": str(uuid.uuid4())[:8],
                        "title": task_title,
                        "task_type": task_type,
                        "requirements": task_desc,
                        "price": task_price,
                        "total": task_total,
                        "remaining": task_total,
                        "region": merchant_region,
                        "merchant": merchant_name,
                        "status": "open",
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    tasks.append(new_task)
                    save_tasks(tasks)
                    st.success(f"✅ 任务发布成功！任务ID: {new_task['id']}")
                    st.rerun()
        
        # 我的任务列表
        st.divider()
        st.subheader("📂 我发布的任务")
        
        tasks = get_tasks()
        my_tasks = [t for t in tasks if t.get("merchant") == merchant_name]
        
        for task in my_tasks:
            with st.expander(f"📌 {task['title']} ({task['remaining']}/{task['total']})"):
                st.write(f"**类型：**{task['task_type']}")
                st.write(f"**单价：**{task['price']}元/条")
                st.write(f"**要求：**{task['requirements']}")
                st.write(f"**状态：**{task['status']}")
                st.write(f"**发布时间：**{task['created_at']}")
    
    with tab2:
        st.subheader("📋 待审核作品")
        
        submissions = get_submissions()
        pending_subs = [s for s in submissions if s.get("status") == "submitted"]
        
        st.write(f"共 {len(pending_subs)} 个作品待审核")
        
        for sub in pending_subs:
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <h4>{sub['task_title']}</h4>
                    <p><b>学生：</b>{sub['student_name']} ({sub['student_school']})</p>
                    <p><b>视频：</b>{sub.get('video_url', '未填写')}</p>
                    <p><b>备注：</b>{sub.get('notes', '无')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"✅ 通过", key=f"approve_{sub['id']}"):
                        # 计算默认结算金额（使用任务单价）
                        task_price = sub.get("task_price", 50)
                        st.info(f"💡 该任务单价：{task_price}元，系统将根据评分自动计算最终金额")
                        
                        # 这里只是简单通过，管理员会在管理端打分
                        if st.button("确认通过", key=f"confirm_{sub['id']}"):
                            for s in submissions:
                                if s["id"] == sub["id"]:
                                    s["status"] = "approved"
                                    s["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            save_submissions(submissions)
                            st.success("✅ 已通过！请在管理端进行打分评分")
                            st.rerun()
                with col2:
                    if st.button(f"❌ 拒绝", key=f"reject_{sub['id']}"):
                        for s in submissions:
                            if s["id"] == sub["id"]:
                                s["status"] = "rejected"
                        save_submissions(submissions)
                        st.warning("❌ 已拒绝")
                        st.rerun()

# ========== 页面：管理员端 ==========
elif role == "👨‍💼 我是管理员":
    st.title("👨‍💼 管理端 - 作品审核打分")
    
    # 数据概览
    tasks = get_tasks()
    submissions = get_submissions()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("任务总数", len(tasks))
    with col2:
        st.metric("作品总数", len(submissions))
    with col3:
        pending_count = len([s for s in submissions if s["status"] == "submitted"])
        st.metric("待审核", pending_count)
    with col4:
        approved = [s for s in submissions if s["status"] == "approved"]
        st.metric("已结算", f"¥{sum(s.get('amount', 0) for s in approved)}")
    
    # 评分说明
    st.info("""
    📋 **FY25创意营销赛评分标准（总分100分）：**
    
    **维度1：创新创意（0-30分）**
    - 独特视角与新颖表达（0-10分）
    - 吸引观众注意力（0-10分）
    - 项目商务策划创新性（0-10分）
    
    **维度2：选题相关性（0-30分）**
    - 准确解读选题方向和受众需求（0-10分）
    - 传达主题精神内涵（0-10分）
    - 主题分析解读的深度和广度（0-10分）
    
    **维度3：呈现表达（0-40分）**
    - 画面质量（清晰度/色彩/构图）（0-10分）
    - 拍摄技巧专业性与艺术性（0-10分）
    - 后期制作（剪辑/特效/音效）（0-10分）
    - 内容文案逻辑与完整性（0-10分）
    
    ---
    **结算等级：**
    - 0-40分：❌ 不合格（结算系数 0）
    - 41-60分：✅ 合格（结算系数 0.8）
    - 61-80分：⭐ 良好（结算系数 1.0）
    - 81-100分：🏆 优秀（结算系数 1.2）
    """)
    
    # 功能标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 作品审核打分", "📋 全部作品", "📊 数据统计", "📈 收入报表"])
    
    # ========== 作品审核打分页面 ==========
    with tab1:
        st.subheader("🎯 作品审核打分")
        
        # 筛选待审核作品
        all_submissions = get_submissions()
        pending_subs = [s for s in all_submissions if s.get("status") == "submitted"]
        
        if not pending_subs:
            st.success("✅ 暂无待审核作品")
        else:
            st.markdown(f"**待审核作品：{len(pending_subs)} 个**")
            
            # 选择要审核的作品
            sub_options = {f"{s['student_name']} - {s['task_title']} ({s.get('student_school', '')})": s for s in pending_subs}
            selected_key = st.selectbox("选择要审核的作品", list(sub_options.keys()))
            
            if selected_key:
                sub = sub_options[selected_key]
                
                # 显示作品信息
                st.markdown("---")
                st.markdown(f"### 📹 作品信息")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**学生姓名：**{sub['student_name']}")
                    st.write(f"**学校：**{sub.get('student_school', '未填写')}")
                    st.write(f"**任务标题：**{sub['task_title']}")
                with col2:
                    st.write(f"**视频链接：**{sub.get('video_url', '未填写')}")
                    st.write(f"**备注：**{sub.get('notes', '无')}")
                    st.write(f"**提交时间：**{sub.get('submitted_at', '未知')}")
                
                # 视频链接可点击
                if sub.get("video_url"):
                    st.markdown(f"[🔗 点击查看视频]({sub['video_url']})")
                
                # 评分区域
                st.markdown("---")
                st.markdown("### ⭐ 评分区域")
                
                # 检查是否已有评分
                existing_score = sub.get("score")
                if existing_score is not None:
                    grade = sub.get("grade", "")
                    grade_emoji = get_grade_emoji(grade)
                    st.warning(f"⚠️ 该作品已评分：{existing_score}分 {grade_emoji} {grade}")
                
                # ========== 评分组件（非表单，实现实时更新）==========
                st.markdown("#### 📋 创意营销赛评分表（总分100分）")
                
                # 获取已有的维度分数
                dim_scores = sub.get("dimension_scores", {})
                
                # ========== 维度1：创新创意（0-30分）==========
                st.markdown("**维度1：创新创意（0-30分）**")
                col_d1_1, col_d1_2, col_d1_3 = st.columns(3)
                with col_d1_1:
                    innovation_1 = st.slider(
                        "① 独特视角与新颖表达",
                        0, 10, 
                        dim_scores.get("innovation_detail", {}).get("独特视角与新颖表达", 5),
                        key=f"d1_1_{sub['id']}",
                        help="视频是否具有独特视角和新颖的表达方式"
                    )
                with col_d1_2:
                    innovation_2 = st.slider(
                        "② 吸引观众注意力",
                        0, 10, 
                        dim_scores.get("innovation_detail", {}).get("吸引观众注意力", 5),
                        key=f"d1_2_{sub['id']}",
                        help="内容能否吸引观众注意力"
                    )
                with col_d1_3:
                    innovation_3 = st.slider(
                        "③ 项目商务策划创新性",
                        0, 10, 
                        dim_scores.get("innovation_detail", {}).get("项目商务策划创新性", 5),
                        key=f"d1_3_{sub['id']}",
                        help="是否符合行业企业实践并进行了创新性策划"
                    )
                innovation_score = innovation_1 + innovation_2 + innovation_3
                st.metric("创新创意小计", f"{innovation_score}/30分")
                
                st.markdown("---")
                
                # ========== 维度2：选题相关性（0-30分）==========
                st.markdown("**维度2：选题相关性（0-30分）**")
                col_d2_1, col_d2_2, col_d2_3 = st.columns(3)
                with col_d2_1:
                    topic_1 = st.slider(
                        "① 准确解读选题方向和受众需求",
                        0, 10, 
                        dim_scores.get("topic_detail", {}).get("解读选题方向和受众需求", 5),
                        key=f"d2_1_{sub['id']}",
                        help="是否准确解读选题方向和受众需求"
                    )
                with col_d2_2:
                    topic_2 = st.slider(
                        "② 传达主题精神内涵",
                        0, 10, 
                        dim_scores.get("topic_detail", {}).get("传达主题精神内涵", 5),
                        key=f"d2_2_{sub['id']}",
                        help="是否准确传达主题精神内涵"
                    )
                with col_d2_3:
                    topic_3 = st.slider(
                        "③ 主题分析解读的深度和广度",
                        0, 10, 
                        dim_scores.get("topic_detail", {}).get("主题分析解读深度和广度", 5),
                        key=f"d2_3_{sub['id']}",
                        help="对主题分析解读的深度和广度"
                    )
                topic_score = topic_1 + topic_2 + topic_3
                st.metric("选题相关性小计", f"{topic_score}/30分")
                
                st.markdown("---")
                
                # ========== 维度3：呈现表达（0-40分）==========
                st.markdown("**维度3：呈现表达（0-40分）**")
                col_d3_1, col_d3_2, col_d3_3, col_d3_4 = st.columns(4)
                with col_d3_1:
                    presentation_1 = st.slider(
                        "① 画面质量（清晰度/色彩/构图）",
                        0, 10, 
                        dim_scores.get("presentation_detail", {}).get("画面质量", 5),
                        key=f"d3_1_{sub['id']}",
                        help="画面清晰度、色彩搭配、构图专业性"
                    )
                with col_d3_2:
                    presentation_2 = st.slider(
                        "② 拍摄技巧专业性与艺术性",
                        0, 10, 
                        dim_scores.get("presentation_detail", {}).get("拍摄技巧专业性与艺术性", 5),
                        key=f"d3_2_{sub['id']}",
                        help="拍摄技巧的专业性与艺术性"
                    )
                with col_d3_3:
                    presentation_3 = st.slider(
                        "③ 后期制作（剪辑/特效/音效）",
                        0, 10, 
                        dim_scores.get("presentation_detail", {}).get("后期制作精致度", 5),
                        key=f"d3_3_{sub['id']}",
                        help="后期制作的精致度（剪辑、特效、音效）"
                    )
                with col_d3_4:
                    presentation_4 = st.slider(
                        "④ 内容文案逻辑与完整性",
                        0, 10, 
                        dim_scores.get("presentation_detail", {}).get("内容文案逻辑与完整性", 5),
                        key=f"d3_4_{sub['id']}",
                        help="内容文案的逻辑结构、完整性、严谨性、真人出镜"
                    )
                presentation_score = presentation_1 + presentation_2 + presentation_3 + presentation_4
                st.metric("呈现表达小计", f"{presentation_score}/40分")
                
                st.markdown("---")
                
                # ========== 总分计算 ==========
                total_score = innovation_score + topic_score + presentation_score
                
                # 实时显示等级和结算信息
                grade = calculate_grade(total_score)
                coefficient = calculate_coefficient(total_score)
                task_price = sub.get("task_price", 50)
                calculated_amount = task_price * coefficient
                
                # 根据等级显示不同样式
                grade_styles = {
                    "优秀": "score-excellent",
                    "良好": "score-good",
                    "合格": "score-pass",
                    "不合格": "score-fail"
                }
                grade_style = grade_styles.get(grade, "")
                
                st.markdown(f"### 📊 总分：{total_score}/100分")
                st.markdown(f"""
                <div class="{grade_style}">
                    <h3 style="margin: 0;">{get_grade_emoji(grade)} 等级：{grade}</h3>
                    <p style="margin: 5px 0;">结算系数：<b>{coefficient}</b></p>
                    <p style="margin: 5px 0;">任务单价：{task_price}元</p>
                    <p style="margin: 5px 0;">结算金额：<b>¥{calculated_amount}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                # 保存各维度分数
                dimension_scores = {
                    "innovation": innovation_score,
                    "topic": topic_score,
                    "presentation": presentation_score,
                    "innovation_detail": {
                        "独特视角与新颖表达": innovation_1,
                        "吸引观众注意力": innovation_2,
                        "项目商务策划创新性": innovation_3
                    },
                    "topic_detail": {
                        "解读选题方向和受众需求": topic_1,
                        "传达主题精神内涵": topic_2,
                        "主题分析解读深度和广度": topic_3
                    },
                    "presentation_detail": {
                        "画面质量": presentation_1,
                        "拍摄技巧专业性与艺术性": presentation_2,
                        "后期制作精致度": presentation_3,
                        "内容文案逻辑与完整性": presentation_4
                    }
                }
                
                # 审核备注
                review_notes = st.text_area("审核备注（可选）", placeholder="填写审核意见...", key=f"notes_{sub['id']}")
                
                # 提交按钮（表单外）
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("💾 提交评分", type="primary", key=f"save_score_{sub['id']}"):
                        # 更新提交数据
                        for s in all_submissions:
                            if s["id"] == sub["id"]:
                                s["score"] = total_score
                                s["grade"] = grade
                                s["coefficient"] = coefficient
                                s["amount"] = calculated_amount
                                s["review_notes"] = review_notes
                                s["dimension_scores"] = dimension_scores
                                s["reviewed_by"] = "管理员"
                                s["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        save_submissions(all_submissions)
                        
                        grade_emoji = get_grade_emoji(grade)
                        st.success(f"💾 评分已保存！{grade_emoji} {grade} | 结算金额：¥{calculated_amount}")
                        st.rerun()
                with col_b:
                    if st.button("✅ 通过并评分", type="secondary", key=f"approve_score_{sub['id']}"):
                        # 更新提交数据
                        for s in all_submissions:
                            if s["id"] == sub["id"]:
                                s["score"] = total_score
                                s["grade"] = grade
                                s["coefficient"] = coefficient
                                s["amount"] = calculated_amount
                                s["review_notes"] = review_notes
                                s["dimension_scores"] = dimension_scores
                                s["reviewed_by"] = "管理员"
                                s["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                s["status"] = "approved"
                                s["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        save_submissions(all_submissions)
                        
                        grade_emoji = get_grade_emoji(grade)
                        st.success(f"✅ 评分已提交并通过！{grade_emoji} {grade} | 结算金额：¥{calculated_amount}")
                        st.rerun()
    
    # ========== 全部作品页面 ==========
    with tab2:
        st.subheader("📋 全部作品")
        
        if submissions:
            # 筛选器
            filter_status = st.selectbox("按状态筛选", ["全部", "pending", "submitted", "approved", "rejected"])
            filter_grade = st.selectbox("按等级筛选", ["全部", "优秀", "良好", "合格", "不合格"])
            
            filtered = submissions
            if filter_status != "全部":
                filtered = [s for s in filtered if s.get("status") == filter_status]
            if filter_grade != "全部":
                filtered = [s for s in filtered if s.get("grade") == filter_grade]
            
            st.write(f"共 {len(filtered)} 个作品")
            
            for sub in filtered:
                grade = sub.get("grade", "未评分")
                grade_emoji = get_grade_emoji(grade)
                
                # 根据等级显示不同颜色
                if grade == "优秀":
                    border_color = "🟣"
                elif grade == "良好":
                    border_color = "🟢"
                elif grade == "合格":
                    border_color = "🟡"
                elif grade == "不合格":
                    border_color = "🔴"
                else:
                    border_color = "⚪"
                
                with st.expander(f"{border_color} {sub['student_name']} - {sub['task_title']} | {grade_emoji} {grade}"):
                    st.json(sub)
        else:
            st.info("暂无作品")
    
    # ========== 数据统计页面 ==========
    with tab3:
        st.subheader("📊 数据统计")
        
        # 按状态统计
        status_counts = {}
        for s in submissions:
            status = s.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.write("**作品状态分布：**")
        if status_counts:
            st.bar_chart(status_counts)
        else:
            st.info("暂无数据")
        
        # 按等级统计
        grade_counts = {}
        for s in submissions:
            grade = s.get("grade", "未评分")
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        st.write("**作品等级分布：**")
        if grade_counts:
            st.bar_chart(grade_counts)
        
        # 按学校统计
        school_counts = {}
        for s in submissions:
            school = s.get("student_school", "未知")
            school_counts[school] = school_counts.get(school, 0) + 1
        
        st.write("**学校分布：**")
        if school_counts:
            st.bar_chart(school_counts)
    
    # ========== 收入报表页面 ==========
    with tab4:
        st.subheader("📈 收入报表")
        
        # 计算收入统计
        approved_subs = [s for s in submissions if s.get("status") == "approved"]
        
        if approved_subs:
            # 按等级统计收入
            grade_income = {}
            grade_count = {}
            for s in approved_subs:
                grade = s.get("grade", "未评分")
                amount = s.get("amount", 0)
                grade_income[grade] = grade_income.get(grade, 0) + amount
                grade_count[grade] = grade_count.get(grade, 0) + 1
            
            st.write("**按等级收入统计：**")
            for grade, income in grade_income.items():
                grade_emoji = get_grade_emoji(grade)
                count = grade_count.get(grade, 0)
                st.write(f"{grade_emoji} {grade}: {count}个作品, 共 ¥{income}")
            
            # 总收入
            total_income = sum(s.get("amount", 0) for s in approved_subs)
            total_count = len(approved_subs)
            avg_income = total_income / total_count if total_count > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总作品数", total_count)
            with col2:
                st.metric("总收入", f"¥{total_income}")
            with col3:
                st.metric("平均收入", f"¥{avg_income:.2f}")
            
            # 详细记录
            st.write("**收入明细：**")
            for s in approved_subs:
                grade = s.get("grade", "未评分")
                grade_emoji = get_grade_emoji(grade)
                st.write(f"- {s['student_name']} | {s['task_title']} | {grade_emoji} {grade} | ¥{s.get('amount', 0)} | {s.get('approved_at', '')}")
        else:
            st.info("暂无已结算作品")

# ========== 页脚 ==========
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🎬 校园星零工平台 MVP v1.1 - 支持管理员打分</p>
    <p>有问题请联系管理员</p>
</div>
""", unsafe_allow_html=True)
