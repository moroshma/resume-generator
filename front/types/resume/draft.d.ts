declare global {
  export interface Idraft {
    id: number;
    step: IStep;
    baseQuestions: IQuestion[];
    generatedQuestions: IQuestion[];
    answersToBasicQuestions: Record<string, string>;
    answersToGeneratedQuestions: Record<string, string>;
    labels: ILabel[];
  }

  export interface ILabel {
    title: string;
    answer: string;
  }

  export interface IStep {
    id: number;
    title: string;
  }
}
