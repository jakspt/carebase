import { Component, inject } from '@angular/core';
import { ActionCard } from '../action-card/action-card';
import { AdminService } from '../services/admin-service';
import { TransactionDialog } from '../transaction-dialog/transaction-dialog';
import { MatDialog } from '@angular/material/dialog';
import { MatCardModule } from '@angular/material/card';

@Component({
  imports: [ActionCard, MatCardModule],
  selector: 'app-admin-page',
  styleUrl: './admin-page.css',
  templateUrl: './admin-page.html',
})
export class AdminPage {
  private adminService = inject(AdminService);
  private dialog = inject(MatDialog);

  migrateDb(): void {
    this.dialog.open(TransactionDialog, {
      width: '450px',
      data: {
        title: 'Migrate Database to MongoDB',
        description:
          'This will migrate all relational MariaDB tables into document collections, normalize subdocuments, and apply compound index optimizations in MongoDB.',
        loadingMessage:
          'Exporting tables, structuring document schemas, and building MongoDB indexes...',
        successMessage:
          'Migration completed! MariaDB records successfully transferred and switched to MongoDB.',
        action: () => this.adminService.migrateDatabase(),
      },
    });
  }

  seedDb(): void {
    this.dialog.open(TransactionDialog, {
      width: '450px',
      data: {
        title: 'Run Database Seeding',
        description:
          'This will generate randomized mock records across all major collections. All existing data will be overwritten!',
        loadingMessage: 'Generating mock entities and populating database...',
        successMessage: 'Database successfully populated with randomized test data.',
        action: () => this.adminService.seedDatabase(),
      },
    });
  }
}
