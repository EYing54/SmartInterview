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
            <label for="avatar_upload" class="upload_button">更换头像</label>
          </div>
        </div>
      </el-card>

      <el-card class="right_card_2">
        <h3>账号信息</h3>
        <p>昵称：{{ data?.nickname }}</p>
        <p>
          新昵称：<input type="text" v-model="newNickname" /><el-button
            @click="uploadNickname"
            type="primary"
            >保存</el-button
          >
        </p>
        <p v-if="newNickname.length > 20">昵称字数超过20辣！</p>
        <p v-else-if="newNickname.length > 0">昵称可用</p>
        <p v-else-if="newNickname.length == 0">请输入新昵称</p>
        <p>用户名：{{ data?.username }}</p>
        <p>当前密码：<input type="password" v-model="currentPassword" /></p>
        <p>新密码：<input type="password" v-model="newPassword" /></p>
        <p v-if="newPassword.length > 50">密码长度超过50辣！</p>
        <p v-else-if="newPassword.length > 0">密码可用</p>
        <p v-else-if="newPassword.length == 0">请输入密码</p>
        <p>
          确认密码：<input type="password" v-model="verifyPassword" />
          <el-button @click="handelModifyPassword" type="primary"
            >确认修改</el-button
          >
        </p>
        <p v-if="verifyPassword.length === 0">请再次输入密码</p>
        <p v-else-if="newPassword !== verifyPassword">
          两次输入的密码不一致哦！
        </p>
        <p v-else-if="newPassword === verifyPassword">恭喜！你终于输对了！</p>
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
import { profileVersion } from "../../stores/avatar";

//获取用户信息
const data = ref(null);
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

//获取头像
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

//修改头像
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
    profileVersion.value++; //若上传头像则更新响应式变量
    await loadUserProfile(); //自动刷新以展示新的头像
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
