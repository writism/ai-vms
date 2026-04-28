export interface Identity {
  id: string;
  name: string;
  identity_type: "EMPLOYEE" | "VISITOR";
  department: string | null;
  employee_id: string | null;
  company: string | null;
  visit_purpose: string | null;
  notes: string | null;
  face_image_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface RecognitionLog {
  id: string;
  camera_id: string;
  identity_id: string | null;
  identity_name: string;
  identity_type: string;
  confidence: number;
  is_registered: boolean;
  created_at: string;
}
