/** Shared TypeScript types mirroring FastAPI response shapes. */

export interface Rental {
  id: number;
  title: string;
  price: string;            // original display string, e.g. "$1,800"
  price_amount: number | null;
  location: string;
  bedrooms?: number | null;
  link: string;
}

export interface RentalListResponse {
  count: number;
  rentals: Rental[];
}

export interface Recommendation extends Rental {
  score: number;
  reasons: string[];
}

export interface RecommendationsResponse {
  count: number;
  recommendations: Recommendation[];
}

export interface BudgetRequest {
  income: number;
  rent: number;
  food: number;
  transport: number;
  utilities: number;
  other: number;
}

export interface BudgetAnalysis {
  income: number;
  expenses: number;
  remaining: number;
  status: "Comfortable" | "Tight but survivable" | "Financially risky";
}

export interface AreaRecommendation {
  area: string;
  vacancy_rate: number;
  score: number;
}

export interface AreaRecommendationsResponse {
  budget: number;
  recommendations: AreaRecommendation[];
}
