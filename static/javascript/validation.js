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

function addEventListeners() {
    const form = document.getElementById('plan_form');
    form.addEventListener('submit', function(event) {
        if (!validateForm()) {
            event.preventDefault();
        }
    });

    const startDateInput = document.getElementById('start_date');
    startDateInput.addEventListener('change', autoUpdateEndDate);
}

document.addEventListener('DOMContentLoaded', addEventListeners);