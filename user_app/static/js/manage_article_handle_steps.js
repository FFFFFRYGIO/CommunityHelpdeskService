let addStepButton = document.getElementById("add-step-button");
let removeStepButton = document.getElementById("remove-step-button");
let stepsFormset = document.getElementById("steps-formset");
let totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]');

addStepButton.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("add-step-button")) {
        e.preventDefault();
        let newStepForm = stepsFormset.lastElementChild.cloneNode(true);

        for (const newStepFormElement of newStepForm.querySelectorAll('input, textarea')) {
            newStepFormElement.value = '';
            newStepFormElement.defaultValue = '';
        }

        newStepForm.innerHTML = newStepForm.innerHTML.replace(/form-\d+/g, "form-" + totalFormsInput.value);
        totalFormsInput.value = parseInt(totalFormsInput.value, 10) + 1;
        newStepForm.innerHTML = newStepForm.innerHTML.replace(/Step \d+/g, "Step " + totalFormsInput.value);

        stepsFormset.appendChild(newStepForm);
    }
});

removeStepButton.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("remove-step-button")) {
        e.preventDefault();
        if (totalFormsInput.value > 1) {
            stepsFormset.lastElementChild.innerHTML = "";
            stepsFormset.removeChild(stepsFormset.lastElementChild);
            totalFormsInput.value = parseInt(totalFormsInput.value, 10) - 1;
        } else {
            alert("You have to have at least 1 step");
        }
    }
});
