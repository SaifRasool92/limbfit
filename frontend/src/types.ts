export interface CrossSection {
  z_mm: number;
  width_mm: number;
  depth_mm: number;
}

export interface SocketParams {
  relief_pct: number;
  wall_mm: number;
  trim_height_mm: number;
  vent_count: number;
  vent_diameter_mm: number;
  hole_diameter_mm: number;
}

export interface Checks {
  is_watertight: boolean;
  volume_cm3: number;
  weight_grams: number;
  cost_estimate: number;
  max_overhang_deg: number;
  min_wall_mm: number;
}

export interface AnalyzeResult {
  sections: CrossSection[];
  socket_glb_url: string;
  socket_stl_url: string;
  debug_overlay_urls?: string[];
  checks: Checks;
  timings_ms: Record<string, number>;
}

export interface RAGSource {
  source: string;
  page: number;
  text: string;
}

export interface ExplainResult {
  rationale: string;
  checklist: string[];
  print_guide: string;
  rag_sources?: RAGSource[];
}

export const DEFAULT_PARAMS: SocketParams = {
  relief_pct: 2.0,
  wall_mm: 3.5,
  trim_height_mm: 10.0,
  vent_count: 6,
  vent_diameter_mm: 4.0,
  hole_diameter_mm: 6.5,
};
