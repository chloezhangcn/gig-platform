"""
校园星零工平台 - Streamlit MVP版本
功能：任务大厅、任务领取、作品提交、收益查看
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

# ========== 页面配置 ==========
st.set_page_config(
    page_title="校园星零工平台",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS让手机端更好看
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
                            "student_name": student_name,
                            "student_phone": student_phone,
                            "student_school": student_school,
                            "status": "pending",
                            "video_url": "",
                            "notes": "",
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
                if my_task.get("approved_at"):
                    st.write(f"**通过时间：**{my_task['approved_at']}")
                    st.write(f"**获得报酬：**💰 {my_task.get('amount', '待结算')} 元")
    
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
                        amount = st.number_input("结算金额", min_value=10, value=50, key=f"amt_{sub['id']}")
                        if st.button("确认通过", key=f"confirm_{sub['id']}"):
                            for s in submissions:
                                if s["id"] == sub["id"]:
                                    s["status"] = "approved"
                                    s["amount"] = amount
                                    s["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            save_submissions(submissions)
                            st.success("✅ 已通过并记录结算金额！")
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
    st.title("👨‍💼 管理端 - 数据中心")
    
    # 数据概览
    tasks = get_tasks()
    submissions = get_submissions()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("任务总数", len(tasks))
    with col2:
        st.metric("作品总数", len(submissions))
    with col3:
        st.metric("待审核", len([s for s in submissions if s["status"] == "submitted"]))
    with col4:
        approved = [s for s in submissions if s["status"] == "approved"]
        st.metric("已结算", f"¥{sum(s.get('amount', 0) for s in approved)}")
    
    # 任务管理
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📋 全部任务", "📤 全部作品", "📊 数据统计"])
    
    with tab1:
        st.subheader("📋 全部任务")
        if tasks:
            for task in tasks:
                with st.expander(f"📌 {task['title']}"):
                    st.json(task)
        else:
            st.info("暂无任务")
    
    with tab2:
        st.subheader("📤 全部作品提交")
        if submissions:
            for sub in submissions:
                with st.expander(f"📌 {sub['task_title']} - {sub['student_name']}"):
                    st.json(sub)
        else:
            st.info("暂无作品")
    
    with tab3:
        st.subheader("📊 数据统计")
        
        # 按状态统计
        status_counts = {}
        for s in submissions:
            status = s.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        st.write("**作品状态分布：**")
        st.bar_chart(status_counts)
        
        # 按大区统计
        region_counts = {}
        for t in tasks:
            region = t.get("region", "unknown")
            region_counts[region] = region_counts.get(region, 0) + 1
        
        st.write("**任务大区分布：**")
        st.bar_chart(region_counts)
        
        # 收入统计
        approved = [s for s in submissions if s.get("status") == "approved"]
        if approved:
            st.write("**已结算记录：**")
            for a in approved:
                st.write(f"- {a['student_name']} | {a['task_title']} | ¥{a.get('amount', 0)} | {a.get('approved_at', '')}")

# ========== 页脚 ==========
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🎬 校园星零工平台 MVP v1.0</p>
    <p>有问题请联系管理员</p>
</div>
""", unsafe_allow_html=True)