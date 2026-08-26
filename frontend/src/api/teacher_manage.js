import request from "../utils/request";

export const getTeacherList = (page, size) => {
  return request.post("/get_teacher_list", {
    page: page,
    size: size,
  });
};

export const deleteAccount = (user_id) => {
  return request.post("/delete_t_account", { user_id: user_id });
};

export const resetAccount = (user_id) => {
  return request.post("/reset_t_account_password", { user_id: user_id });
};
