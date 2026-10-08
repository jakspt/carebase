import { Component, computed, inject, signal } from '@angular/core';
import { CurrencyPipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { BarChartModule } from '@swimlane/ngx-charts';
import { DoctorService } from '../services/doctor-service';
import { DoctorEarnings } from '../models/models';

interface ChartDataItem {
  name: string;
  value: number;
}

@Component({
  imports: [
    CurrencyPipe,
    MatCardModule,
    MatFormFieldModule,
    MatSelectModule,
    MatTableModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatPaginatorModule,
    BarChartModule,
  ],
  selector: 'app-doctor-report',
  styleUrl: './doctor-report.css',
  templateUrl: './doctor-report.html',
})
export class DoctorReport {
  private readonly doctorService = inject(DoctorService);

  readonly currentYear = new Date().getFullYear();
  readonly availableYears: number[] = Array.from(
    { length: this.currentYear - 2020 + 1 },
    (_, i) => this.currentYear - i
  );

  readonly selectedYear = signal<number>(this.currentYear);

  readonly reportResource = this.doctorService.getReport(this.selectedYear);

  readonly reportData = computed<DoctorEarnings[]>(() => {
    if (this.reportResource.hasValue()) {
      return this.reportResource.value()?.data ?? [];
    }
    return [];
  });

  // Top 10 doctors with clean names (without IDs) for optimal bar readability
  readonly chartData = computed<ChartDataItem[]>(() => {
    const list = this.reportData();
    const map = new Map<number, { name: string; total: number }>();
    for (const row of list) {
      const existing = map.get(row.id);
      if (existing) {
        existing.total += row.totalCosts;
      } else {
        map.set(row.id, {
          name: row.name,
          total: row.totalCosts,
        });
      }
    }
    return Array.from(map.values())
      .map((item) => ({ name: item.name, value: item.total }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
  });

  // Table pagination
  readonly pageSize = signal<number>(10);
  readonly pageIndex = signal<number>(0);

  readonly pagedReportData = computed<DoctorEarnings[]>(() => {
    const list = this.reportData();
    const start = this.pageIndex() * this.pageSize();
    return list.slice(start, start + this.pageSize());
  });

  readonly displayedColumns: string[] = [
    'id',
    'name',
    'specialty',
    'department',
    'year',
    'totalCosts',
  ];

  readonly customColorScheme: any = {
    domain: [
      '#0284c7',
      '#0ea5e9',
      '#38bdf8',
      '#0369a1',
      '#2563eb',
      '#4f46e5',
      '#6366f1',
      '#8b5cf6',
    ],
  };

  onYearChange(year: number): void {
    this.selectedYear.set(year);
    this.pageIndex.set(0);
  }

  onPageChange(event: PageEvent): void {
    this.pageSize.set(event.pageSize);
    this.pageIndex.set(event.pageIndex);
  }
}
