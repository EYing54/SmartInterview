import request from "../utils/request";

export const loginAPI = (username, password) => {
  return request.post("/login", { username: username, password: password });
};

export const getUserProfile = () => {
  return request.post("/get_user_profile");
};

export const uploadAvatar = (avatar_file) => {
  const formData = new FormData();
  formData.append("avatar", avatar_file);
  return request.post("/upload_avatar", formData);
};

export const getUserAvatar = () => {
  return request.get("/get_user_avatar", {
    responseType: "blob",
  });
};

export const modifyPost = (new_post) => {
  return request.post("/modify_post", { new_post: new_post });
};

export const modifyPassword = (old_password, new_password) => {
  return request.post("/modify_password", {
    old_password: old_password,
    new_password: new_password,
  });
};

export const modifyNickname = (new_nickname) => {
  return request.post("/modify_nickname", { new_nickname: new_nickname });
};
