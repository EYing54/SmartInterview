import request from "../utils/request";

export const getTeacherList = (page, size) => {
  return request.post("/get_teacher_list", {
    page: page,
    size: size,
  });
};

export const deleteAccount = (userIds) => {
  return request.post("/delete_t_account", { user_ids: userIds });
};

export const resetAccount = (userId) => {
  return request.post("/reset_t_account_password", { user_id: userId });
};
