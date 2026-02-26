function validateForm() {
    const startDateInput = document.getElementById('start_date').value;
    const endDateInput = document.getElementById('end_date').value;
    const errorMessageElement = document.getElementById('form-error-message');

    startDate = new Date(startDateInput);
    endDate = new Date(endDateInput);

    if (startDate > endDate) {
        errorMessageElement.textContent = "Start date must be before end date.";
        errorMessageElement.hidden = false;
        return false;
    } else if ((endDate - startDate) / (1000 * 60 * 60 * 24) > 7) {
        errorMessageElement.textContent = "Date range cannot exceed 7 days.";
        errorMessageElement.hidden = false;
        return false;
    } else {
        errorMessageElement.hidden = true;
        return true;
    }
}