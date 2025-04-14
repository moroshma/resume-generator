export interface IStep {
  id: number;
  title: string;
}

export interface ILabel {
  title: string;
  answer: string;
}

export interface Idraft {
  id: number;
  step: IStep;
  baseQuestions: IQuestion[];
  generatedQuestions: IQuestion[];
  answers: Record<string, string>;
  labels: ILabel[];
}
