describe('template spec', () => {

    it('Register Test', () => {
        cy.visit('http://127.0.0.1:8000/registration/register/');
        cy.get('#id_username').type('testuser');
        cy.get('#id_password1').type('ph1shstix!');
        cy.get('#id_password2').type('ph1shstix!');
        cy.get('.registration_button').click();
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/registration/login/'
            );
        });
        cy.cleanup_user('testuser');
    });

    afterEach(() => {
        cy.cleanup_user('testuser');
    });

});
