function validateForm() {
    const startDateInput = document.getElementById('start_date').value;
    const endDateInput = document.getElementById('end_date').value;
    const errorMessageElement = document.getElementById('form-error-message');

    const startDate = new Date(startDateInput);
    const endDate = new Date(endDateInput);

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

function autoUpdateEndDate() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    let newEndDate = new Date(startDateInput.value);

    if (isNaN(newEndDate.getTime())) {
        return;
    }

    newEndDate.setDate(newEndDate.getDate() + 7);
    endDateInput.value = newEndDate.toISOString().split('T')[0];

    return;
}

function updateWeek() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    let startDate = new Date(startDateInput.value);
    let endDate = new Date(endDateInput.value);

    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        return;
    }

    if (this.id === 'previous-week-button') {
        startDate.setDate(startDate.getDate() - 7);
        endDate.setDate(endDate.getDate() - 7);
    } else if (this.id === 'next-week-button') {
        startDate.setDate(startDate.getDate() + 7);
        endDate.setDate(endDate.getDate() + 7);
    }

    startDateInput.value = startDate.toISOString().split('T')[0];
    endDateInput.value = endDate.toISOString().split('T')[0];
}

function addEventListeners() {
    const form = document.getElementById('plan_form');
    form.addEventListener('submit', function(event) {
        if (!validateForm()) {
            event.preventDefault();
        }
    });

    const startDateInput = document.getElementById('start_date');
    startDateInput.addEventListener('change', autoUpdateEndDate);

    const previousWeekButton = document.getElementById('previous-week-button');
    const nextWeekButton = document.getElementById('next-week-button');
    previousWeekButton.addEventListener('click', updateWeek);
    nextWeekButton.addEventListener('click', updateWeek);
}

document.addEventListener('DOMContentLoaded', addEventListeners);