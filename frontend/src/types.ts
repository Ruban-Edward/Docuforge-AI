export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  role_name: string;
  department_id?: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface Department {
  id: string;
  name: string;
  code?: string;
  description?: string;
  parent_department_id?: string;
  is_active: boolean;
}

export interface Template {
  id: string;
  name: string;
  code: string;
  description?: string;
  category?: string;
  is_active: boolean;
}

export interface Stats {
  total_users: number;
  total_templates: number;
  total_documents: number;
  total_departments: number;
}
