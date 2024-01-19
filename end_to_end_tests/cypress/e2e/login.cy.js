describe('template spec', () => {

    beforeEach(() => {
        cy.register_user('testuser', 'ph1shstix!');
    });

    it('Login Test', () => {
        cy.visit('http://127.0.0.1:8000/registration/login/');
        cy.get('#id_username').type('testuser');
        cy.get('#id_password').type('ph1shstix!');
        cy.get('.registration_button').click();
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/user_app/home/'
            );
        });
    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.cleanup_user('testuser');
    });

});
