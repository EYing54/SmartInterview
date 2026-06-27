import request from "../utils/request";

export const queryMyClasses = () => {
  return request.post("/query_my_classes");
};

export const queryStudents = (classId) => {
  return request.post("/query_class_students", { class_id: classId });
};

export const removeStudent = (studentId) => {
  return request.post("/remove_student", { student_id: studentId });
};

export const deleteClass = (classId) => {
  return request.post("/delete_class", { class_id: classId });
};

export const createClass = (className, classIntroduce) => {
  return request.post("/create_class", {
    class_name: className,
    class_introduce: classIntroduce,
  });
};

export const updateClassInformation = (classId, className, classIntroduce) => {
  return request.post("/update_class_information", {
    class_id: classId,
    enter_class_name: className,
    enter_class_introduce: classIntroduce,
  });
};

export const getStudentInterviewHistory = (studentId) => {
  return request.post("/get_s_interviews_history", { student_id: studentId });
};

export const getStudentInterviewDetail = (interviewId) => {
  return request.post("/get_student_interview", { interview_id: interviewId });
};
