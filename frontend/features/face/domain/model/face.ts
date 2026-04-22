export interface Identity {
  id: string;
  name: string;
  identity_type: "INTERNAL" | "EXTERNAL" | "VIP" | "BLACKLIST";
  department: string | null;
  employee_id: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
}
