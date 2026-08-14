/** Shared TypeScript types mirroring FastAPI response shapes. */

export interface Rental {
  id: number;
  title: string;
  price: string;            // original display string, e.g. "$1,800"
  price_amount: number | null;
  location: string;
  bedrooms?: number | null;
  property_type?: string | null;
  link: string;
  /** "craigslist" for scraped rows, "demo" for seeded sample data. */
  source?: string | null;
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

export interface VacancyPoint {
  year: number;
  vacancy_rate: number;
}

export interface VacancyTrend {
  area: string;
  zones_matched: string[];
  series: VacancyPoint[];
}

export interface MarketStats {
  area: string;
  average_vacancy: number;
  latest_year: number;
  latest_vacancy: number;
}

export interface ScamAnalysis {
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  reasons: string[];
}

/** Several endpoints return {error: "..."} with a 200 instead of raising. */
export interface ApiErrorShape {
  error: string;
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
