export type UserRole = 'admin' | 'leader' | 'member'

export interface User {
  id: string
  email: string
  role: UserRole
  created_at: string
}
