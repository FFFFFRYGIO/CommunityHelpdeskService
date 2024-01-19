// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

Cypress.Commands.add('register_user', (username, password) => {
    cy.visit('http://127.0.0.1:8000/registration/register/');
    cy.get('#id_username').type(username);
    cy.get('#id_password1').type(password);
    cy.get('#id_password2').type(password);
    cy.get('.registration_button').click();

    cy.location().should((loc) => {
        expect(loc.href).to.eq(
            'http://127.0.0.1:8000/registration/login/'
        );
    });
});

Cypress.Commands.add('login_user', (username, password) => {
    cy.visit('http://127.0.0.1:8000/registration/login/');
    cy.get('#id_username').type(username);
    cy.get('#id_password').type(password);
    cy.get('.registration_button').click();
    cy.location().should((loc) => {
        expect(loc.href).to.eq(
            'http://127.0.0.1:8000/user_app/home/'
        );
    });
});

Cypress.Commands.add('cleanup_user', (username) => {
    cy.visit('http://127.0.0.1:8000/admin/login/?next=/admin/');
    cy.get('#id_username').type('fffffrygio');
    cy.get('#id_password').type('ph1shstix!');
    cy.get('input[type="submit"]').click();
    cy.visit('http://127.0.0.1:8000/admin/auth/user/');
    cy.get('a').contains(username).invoke('attr', 'href').then(href => {
        cy.visit(`http://127.0.0.1:8000${href}`);
    });
    cy.get('a.deletelink').invoke('attr', 'href').then(href => {
        cy.visit(`http://127.0.0.1:8000${href}`);
    });
    cy.get('input[type="submit"]').click();
    cy.visit('http://127.0.0.1:8000/registration/logout');
});
