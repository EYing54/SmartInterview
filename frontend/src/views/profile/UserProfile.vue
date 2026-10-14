<template>
  <div class="profile_layout">
    <el-card class="left_card">左侧导航栏</el-card>
    <div class="right_container">
      <el-card class="right_card_1">
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
            <label for="avatar_upload" class="upload_button"> 更换头像 </label>
          </div>
        </div>
      </el-card>

      <el-card class="right_card_2">
        <h3>账号信息</h3>
        <p>用户名：{{ data?.username }}</p>
        <p>昵称：{{ data?.nickname }}</p>
      </el-card>
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
  modifyPost,
  modifyPassword,
  modifyNickname,
} from "../../api/user";
import { avatarVersion } from "../../stores/avatar";

const data = ref(null);
//获取用户信息
const loadUserProfile = async () => {
  try {
    const res = await getUserProfile();
    data.value = res.data.data;
    console.log(data.value);
    const avatarPath = res.data.data.avatar_path;
    if (avatarPath) {
      getAvatarURL(); //若用户未设置头像则不访问接口以节省资源
    }
  } catch (error) {
    console.log("获取用户信息失败：", error);
    ElMessage.error("获取用户信息失败");
  }
};

const url = ref("");
const getAvatarURL = async () => {
  try {
    const res = await getUserAvatar();
    if (url.value) {
      URL.revokeObjectURL(url.value); // 新头像获取成功后，释放旧的URL
    }
    console.log(res.data);
    url.value = URL.createObjectURL(res.data); //使用URL.createObjectURL生成一个临时的url供<el-avatar>使用
  } catch (error) {
    console.log(error);
  }
};

const handleAvatarChange = async (event) => {
  //event用来接收change事件
  const avatarFile = event.target.files[0]; //从change是事件中拿到用户上传的头像文件
  if (!avatarFile) {
    console.log("用户未上传图片！");
    return;
  }
  console.log(avatarFile);
  try {
    const res = await uploadAvatar(avatarFile);
    console.log(res.data.msg);
    ElMessage.success("头像上传成功！");
    avatarVersion.value++; //若上传头像则更新响应式变量
    await loadUserProfile(); //自动刷新以展示新的头像
  } catch (error) {
    ElMessage.error("头像上传失败！");
    console.log(error);
  }
};

onMounted(() => {
  loadUserProfile();
});

onUnmounted(() => {
  if (url.value) {
    URL.revokeObjectURL(url.value);
  } //避免头像地址为空时还尝试释放
});
</script>

<style scoped>
.profile_layout {
  display: flex;
  gap: 5px;
}

.left_card {
  width: 220px;
}

.right_container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

/* 头像和右侧信息横向排列 */
.avatar_content {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px 4px;
}

/* 头像保持原有尺寸 */
.avatar_content .el-avatar {
  flex-shrink: 0;
}

/* 右侧文字和按钮纵向排列 */
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

/* 隐藏原生文件选择框 */
#avatar_upload {
  display: none;
}

/* 自定义更换头像按钮 */
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
</style>
