export const filterSubjectList = (
  subjectsList: Array<Record<string, string | undefined>>,
  subjectType: string
) => {
  return subjectsList
    .filter((subject) => subject.type === subjectType)
    .map((subject) => ({
      subjectId: subject.subject_id,
      subjectName: subject.subject_name
    }))
    .sort((a, b) => a.subjectName.localeCompare(b.subjectName))
}
