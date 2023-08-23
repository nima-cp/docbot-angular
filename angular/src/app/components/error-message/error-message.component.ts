import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

/**
 * Displays an error message to the user and provides an option to close it.
 */
@Component({
  selector: 'app-error-message',
  templateUrl: './error-message.component.html',
  styleUrls: ['./error-message.component.css'],
})
export class ErrorMessageComponent implements OnChanges {
  /**
   * The error message to be displayed.
   */
  @Input() errorMessage?: string;

  /**
   * Controls the visibility of the error message.
   */
  showErrorMessage: boolean = true;

  /**
   * Responds to changes in the errorMessage input.
   * Shows the error message if it is present, otherwise hides it.
   * @param {SimpleChanges} changes - The changes detected in the component inputs.
   */
  ngOnChanges(changes: SimpleChanges) {
    if (changes && this.errorMessage) {
      this.showErrorMessage = true;
    } else {
      this.showErrorMessage = false;
    }
  }

  /**
   * Closes the error message by hiding it and clearing the error message content.
   */
  error_message_close(): void {
    this.showErrorMessage = false;
    this.errorMessage = '';
  }
}
