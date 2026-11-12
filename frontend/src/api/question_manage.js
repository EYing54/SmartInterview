import request from "../utils/request";

export const getQuestionList = (page, size) => {
  return request.post("/get_questions", {
    page: page,
    size: size,
  });
};

export const addQuestions = (question, answer, tagIds) => {
  return request.post("/add_questions", {
    question: question,
    answer: answer,
    tag_ids: tagIds,
  });
};
export const deleteQuestions = (questionId) => {
  return request.post("/delete_question", { question_id: questionId });
};
