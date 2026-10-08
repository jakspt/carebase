import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { Service, inject } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { DbStatus } from '../models/models';

@Service()
export class AdminService {
  private readonly http = inject(HttpClient);

  readonly statusResource = httpResource<DbStatus>(() => '/api/status');

  seedDatabase(): Observable<{ success: boolean; message: string }> {
    return this.http
      .post<{ success: boolean; message: string }>('/api/admin/seed', {})
      .pipe(tap(() => this.statusResource.reload()));
  }

  migrateDatabase(): Observable<{ success: boolean; message: string }> {
    return this.http
      .post<{ success: boolean; message: string }>('/api/admin/migrate', {})
      .pipe(tap(() => this.statusResource.reload()));
  }

  refreshStatus(): void {
    this.statusResource.reload();
  }
}
