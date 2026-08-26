import request from "../utils/request";

export const getStudentList = (page, size) => {
  return request.post("/get_student_list", {
    page: page,
    size: size,
  });
};

export const deleteAccount = (user_id) => {
  return request.post("/delete_s_account", { user_id: user_id });
}; //user_id的数据类型是数组

export const resetAccount = (user_id) => {
  return request.post("/reset_s_account_password", { user_id: user_id });
}; //user_id的数据类型也是数组
