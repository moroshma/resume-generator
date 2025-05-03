declare global {
  export interface IDraft {
    id: number;
    step: IStep;
    baseQuestions: IQuestion[];
    generatedQuestions: IQuestion[];
    answersToBasicQuestions: Record<string, string>;
    answersToGeneratedQuestions: Record<string, string>;
    labels: ILabel[];
    pdf: File | undefined;
  }

  export interface ILabel {
    title: string;
    answer: string;
  }

  export interface IStep {
    id: number;
    title: string;
    component: ShallowRef<Component>;
  }

  export interface IDraftProgress {
    totalSteps: number;
    step: IStep;
  }
}
export {};
