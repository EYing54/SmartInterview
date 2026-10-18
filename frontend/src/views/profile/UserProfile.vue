<template>
  <div class="profile_layout">
    <el-card class="left_card">
      <h3>个人中心</h3>
      <div class="nav_list">
        <button @click="scrollToSection('avatar')">
          <el-icon><UserFilled /></el-icon>
          我的头像
        </button>
        <button @click="scrollToSection('name')">
          <el-icon><Postcard /></el-icon>
          我的姓名
        </button>
        <button @click="scrollToSection('nickname')">
          <el-icon><EditPen /></el-icon>
          我的昵称
        </button>
        <button @click="scrollToSection('password')">
          <el-icon><Lock /></el-icon>
          修改密码
        </button>
        <button v-if="isStudent" @click="scrollToSection('post')">
          <el-icon><Briefcase /></el-icon>
          意向岗位
        </button>
      </div>
    </el-card>

    <div ref="scrollContainer" class="right_container">
      <!-- 我的头像 -->
      <div id="avatar" class="setting_section">
        <h3 class="section_title">我的头像</h3>
        <el-card class="setting_card">
          <div class="avatar_content">
            <el-avatar :size="80" :src="url">头像</el-avatar>
            <div class="avatar_details">
              <div class="avatar_title">个人头像</div>
              <p class="avatar_description">
                仅支持 .png .jpg .jpeg .webp 格式的图片
              </p>
              <input
                id="avatar_upload"
                type="file"
                @change="handleAvatarChange"
              />
              <label for="avatar_upload" class="upload_button">
                更换头像
              </label>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 我的姓名 -->
      <div id="name" class="setting_section">
        <h3 class="section_title">我的姓名</h3>
        <el-card class="setting_card">
          <p class="info_row">
            <span class="field_label">姓名：</span>
            <span>{{ data?.real_name }}</span>
          </p>
          <p class="info_row">
            <span class="field_label">用户名：</span>
            <span>{{ data?.username }}</span>
          </p>
        </el-card>
      </div>

      <!-- 我的昵称 -->
      <div id="nickname" class="setting_section">
        <h3 class="section_title">我的昵称</h3>
        <el-card class="setting_card">
          <p class="info_row">
            <span class="field_label">当前昵称：</span>
            <span>{{ data?.nickname }}</span>
          </p>
          <p class="form_row">
            <span class="field_label">新昵称：</span>
            <input type="text" v-model="newNickname" />
            <el-button @click="uploadNickname" type="primary"> 保存 </el-button>
          </p>
          <p v-if="newNickname.length > 20" class="hint error">
            昵称字数超过20辣！
          </p>
          <p v-else-if="newNickname.length > 0" class="hint success">
            昵称可用
          </p>
          <p v-else class="hint waiting">请输入新昵称</p>
        </el-card>
      </div>

      <!-- 修改密码 -->
      <div id="password" class="setting_section">
        <h3 class="section_title">修改密码</h3>
        <el-card class="setting_card">
          <p class="form_row">
            <span class="field_label">当前密码：</span>
            <input type="password" v-model="currentPassword" />
          </p>
          <p class="form_row">
            <span class="field_label">新密码：</span>
            <input type="password" v-model="newPassword" />
          </p>
          <p v-if="newPassword.length > 50" class="hint error">
            密码长度超过50辣！
          </p>
          <p v-else-if="newPassword.length > 0" class="hint success">
            密码可用
          </p>
          <p v-else class="hint waiting">请输入密码</p>
          <p class="form_row">
            <span class="field_label">确认密码：</span>
            <input type="password" v-model="verifyPassword" />
            <el-button @click="handelModifyPassword" type="primary">
              保存
            </el-button>
          </p>
          <p v-if="verifyPassword.length === 0" class="hint waiting">
            请再次输入密码
          </p>
          <p v-else-if="newPassword !== verifyPassword" class="hint error">
            两次输入的密码不一致哦！
          </p>
          <p v-else class="hint success">恭喜！你终于输对了！</p>
        </el-card>
      </div>

      <!-- 意向岗位 -->
      <div v-if="isStudent" id="post" class="setting_section">
        <h3 class="section_title">意向岗位</h3>
        <el-card class="setting_card">
          <p class="info_row">
            <span class="field_label">当前岗位：</span>
            <span>{{ data?.post }}</span>
          </p>
          <div class="form_row">
            <span class="field_label">修改岗位：</span>
            <el-select v-model="selectedPost" placeholder="请选择你的意向岗位">
              <el-option
                v-for="name in jobPositions"
                :key="name"
                :label="name"
                :value="name"
              />
            </el-select>
            <el-button @click="handelModifyPost" type="primary">
              保存
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import {
  getUserProfile,
  uploadAvatar,
  getUserAvatar,
  getJobPositions,
  modifyPost,
  modifyPassword,
  modifyNickname,
} from "../../api/user";
import { profileVersion } from "../../stores/avatar";
import {
  UserFilled,
  Postcard,
  EditPen,
  Lock,
  Briefcase,
} from "@element-plus/icons-vue";

const isStudent = ref(localStorage.getItem("role") === "0");
const scrollContainer = ref(null);

const scrollToSection = (id) => {
  const container = scrollContainer.value;
  const target = container.querySelector(`#${id}`);
  if (!target) return;

  const top =
    target.getBoundingClientRect().top -
    container.getBoundingClientRect().top +
    container.scrollTop;

  container.scrollTo({
    top: top,
    behavior: "smooth",
  });
};

//获取用户信息
const data = ref(null);
const loadUserProfile = async () => {
  try {
    const res = await getUserProfile();
    data.value = res.data.data;
    console.log(data.value);

    const avatarPath = res.data.data.avatar_path;
    if (avatarPath) {
      getAvatarURL();
    }
  } catch (error) {
    console.log("获取用户信息失败：", error);
    ElMessage.error("获取用户信息失败");
  }
};

//获取头像
const url = ref("");
const getAvatarURL = async () => {
  try {
    const res = await getUserAvatar();
    if (url.value) {
      URL.revokeObjectURL(url.value);
    }
    console.log(res.data);
    url.value = URL.createObjectURL(res.data);
  } catch (error) {
    console.log(error);
  }
};

//修改头像
const handleAvatarChange = async (event) => {
  const avatarFile = event.target.files[0];
  if (!avatarFile) {
    console.log("用户未上传图片！");
    return;
  }
  console.log(avatarFile);

  try {
    const res = await uploadAvatar(avatarFile);
    console.log(res.data.msg);
    ElMessage.success("头像上传成功！");
    profileVersion.value++;
    await loadUserProfile();
  } catch (error) {
    ElMessage.error("头像上传失败！");
    console.log(error);
  }
};

//修改昵称
const newNickname = ref("");
const uploadNickname = async () => {
  try {
    if (newNickname.value.length > 20) {
      ElMessage.error("昵称修改失败！");
      return;
    }
    if (newNickname.value.length == 0) {
      ElMessage.error("昵称不能为空！");
      return;
    }
    if (newNickname.value == data.value) {
      ElMessage.error("新昵称与旧昵称相同！");
    }

    const res = await modifyNickname(newNickname.value);
    console.log(res.data.msg);
    profileVersion.value++;
    await loadUserProfile();
    ElMessage.success("昵称修改成功！");
  } catch (error) {
    console.log(error);
    ElMessage.error("昵称修改失败！");
  }
};

//修改密码
const currentPassword = ref("");
const newPassword = ref("");
const verifyPassword = ref("");

const handelModifyPassword = async () => {
  try {
    if (newPassword.value !== verifyPassword.value) {
      ElMessage.error("两次密码不一致");
      return;
    }
    if (newPassword.value.length > 50) {
      ElMessage.error("密码长度超过50辣！");
      return;
    }
    if (
      currentPassword.value.length === 0 ||
      newPassword.value.length === 0 ||
      verifyPassword.value.length === 0
    ) {
      ElMessage.error("请完整填写密码信息！");
      return;
    }

    const res = await modifyPassword(currentPassword.value, newPassword.value);
    console.log(res.data.msg);
    ElMessage.success("密码修改成功！");
  } catch (error) {
    console.log(error);
    console.log(error.response?.data?.msg);
    ElMessage.error(error.response?.data?.msg || "密码修改失败！");
  }
};

//获取所有可用的岗位名称
const selectedPost = ref("");
const jobPositions = ref([]);

const loadPositions = async () => {
  const res = await getJobPositions();
  jobPositions.value = res.data.data;
};

//修改意向岗位
const handelModifyPost = async () => {
  try {
    if (!selectedPost.value) {
      ElMessage.error("请选择意向岗位！");
      return;
    }
    if (selectedPost.value === data.value.post) {
      ElMessage.error("不要重复选择哦！");
      return;
    }

    const res = await modifyPost(selectedPost.value);
    console.log(res.data.msg);
    ElMessage.success("意向岗位修改成功！");
    await loadUserProfile();
  } catch (error) {
    console.log(error);
    ElMessage.error(error.response?.data?.msg || "意向岗位修改失败！");
  }
};

onMounted(() => {
  loadUserProfile();
  if (isStudent.value) {
    loadPositions();
  }
});

onUnmounted(() => {
  if (url.value) {
    URL.revokeObjectURL(url.value);
  }
});
</script>

<style scoped>
/* 整体布局 */
.profile_layout {
  display: flex;
  gap: 16px;
  height: calc(100vh - 100px);
  overflow: hidden;
  padding: 10px;
  box-sizing: border-box;
}

/* 左侧导航栏 */
.left_card {
  width: 220px;
  height: 100%;
  flex-shrink: 0;
  box-sizing: border-box;
  border-radius: 10px;
}

.left_card :deep(.el-card__body) {
  height: 100%;
  padding: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.left_card h3 {
  margin: 0;
  padding: 22px 0;
  border-bottom: 1px solid #409eff;
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  color: #409eff;
}

.nav_list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  padding: 0 20px;
}

.nav_list button {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 18px 10px 22px;
  border: none;
  background: transparent;
  color: #606266;
  font-size: 15px;
  cursor: pointer;
}

.nav_list .el-icon {
  font-size: 18px;
}

.nav_list button::before,
.nav_list button::after {
  content: "";
  position: absolute;
  bottom: 4px;
  left: 20%;
  width: 60%;
}

.nav_list button::before {
  height: 1px;
  background: #dcdfe6;
}

.nav_list button::after {
  height: 2px;
  background: #409eff;
  transform: scaleX(0);
  transform-origin: center;
  transition: transform 0.3s ease;
}

.nav_list button:hover {
  color: #409eff;
}

.nav_list button:hover::after {
  transform: scaleX(1);
}

/* 右侧滚动区域 */
.right_container {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
  scroll-behavior: smooth;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 10px 12px 20px;
  box-sizing: border-box;
}

.right_container::-webkit-scrollbar {
  display: none;
}

/* 标题在卡片外 */
.setting_section {
  flex-shrink: 0;
}

.section_title {
  margin: 0 0 12px;
  padding-left: 12px;
  border-left: 4px solid #409eff;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

/* 设置卡片 */
.setting_card {
  border-radius: 10px;
}

/* 所有信息行和表单行使用相同的布局 */
.info_row,
.form_row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 16px;
  font-size: 15px;
  line-height: 1.5;
}

.info_row:last-child,
.form_row:last-child {
  margin-bottom: 0;
}

/* 固定标签宽度 */
.field_label {
  flex: 0 0 90px;
  white-space: nowrap;
  text-align: left;
}

/* 不可编辑的信息 */
.info_row {
  color: #303133;
}

/* 输入框统一尺寸 */
.form_row input:not([type="file"]) {
  width: 200px;
  height: 34px;
  box-sizing: border-box;
  padding: 6px 9px;
  border: 1px solid #dcdfe6;
  border-radius: 5px;
  font-size: 14px;
  outline: none;
}

.form_row input:not([type="file"]):focus {
  border-color: #409eff;
}

/* 岗位下拉框与普通输入框等宽 */
.form_row :deep(.el-select) {
  width: 200px;
  flex: 0 0 200px;
}

.form_row :deep(.el-select__wrapper) {
  min-height: 34px;
}

/* 按钮紧跟输入框 */
.form_row :deep(.el-button) {
  flex-shrink: 0;
  margin: 0;
  height: 34px;
}

/* 实时提示：与输入框左侧对齐 */
.hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: -6px 0 18px 102px;
  font-size: 12px;
  line-height: 1.5;
}

/* 未输入 */
.hint.waiting {
  color: #e6a23c;
}

.hint.waiting::before {
  content: "●";
  font-size: 9px;
}

/* 输入符合要求 */
.hint.success {
  color: #67c23a;
}

.hint.success::before {
  content: "✓";
  font-size: 14px;
  font-weight: 600;
}

/* 输入不符合要求 */
.hint.error {
  color: #f56c6c;
}

.hint.error::before {
  content: "✕";
  font-size: 12px;
  font-weight: 600;
}

/* 头像区域保留原有样式 */
.avatar_content {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px 4px;
}

.avatar_content .el-avatar {
  flex-shrink: 0;
}

.avatar_details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.avatar_title {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
}

.avatar_description {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

#avatar_upload {
  display: none;
}

.upload_button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border: 1px solid #d9e6f5;
  border-radius: 8px;
  background-color: #f0f7ff;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.upload_button:hover {
  background-color: #e1efff;
}

.setting_card .hint:last-child {
  margin-bottom: 0;
}

.info_row span:last-child {
  color: #909399;
}
</style>
