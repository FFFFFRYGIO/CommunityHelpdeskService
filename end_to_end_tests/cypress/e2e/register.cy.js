describe('template spec', () => {

    it('Register Test', () => {
        cy.visit('http://127.0.0.1:8000/registration/register/');
        cy.fixture('user').then(user => {
            cy.get('#id_username').type(user.username);
            cy.get('#id_password1').type(user.password);
            cy.get('#id_password2').type(user.password);
        });
        cy.get('.registration_button').click();
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/registration/login/'
            );
        });
    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.fixture('user').then(user => {
            cy.cleanup_user(user.username);
        });
    });

});
