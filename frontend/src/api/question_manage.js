import request from "../utils/request";

export const getQuestionList = (page, size) => {
  return request.post("/get_questions", {
    page: page,
    size: size,
  });
};
