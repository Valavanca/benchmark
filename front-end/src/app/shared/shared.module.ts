import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';


// Animation
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
// Material
import {
  MatButtonModule,
  MatCheckboxModule,
  MatCardModule,
  MatListModule,
  MatIconModule,
  MatTabsModule,
  MatTooltipModule,
  MatGridListModule,
  MatProgressBarModule,
  MatSelectModule
} from '@angular/material';

@NgModule({
  imports: [
    CommonModule,
    BrowserAnimationsModule,
    MatButtonModule,
    MatCheckboxModule,
    MatCardModule,
    MatListModule,
    MatIconModule,
    MatTabsModule,
    MatTooltipModule,
    MatGridListModule,
    MatProgressBarModule,
    MatSelectModule
  ],
  declarations: [],
  exports: [
    CommonModule,
    BrowserAnimationsModule,
    MatButtonModule,
    MatCheckboxModule,
    MatCardModule,
    MatListModule,
    MatIconModule,
    MatTabsModule,
    MatTooltipModule,
    MatGridListModule,
    MatProgressBarModule,
    MatSelectModule]
})
export class SharedModule { }