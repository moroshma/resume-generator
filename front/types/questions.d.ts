// types/questions.d.ts
export interface IQuestion {
    id: string | number
    type: QuestionType
    text: string
    options?: string[]
    required?: boolean
  }
  
  export type QuestionType = 
    | 'Text' 
    | 'Select' 
    | 'Multi' 
    | 'Rating'