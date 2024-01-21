describe('template spec', () => {

    beforeEach(() => {
        cy.fixture('user').then(user => {
            cy.register_user(user.username, user.password);
        });
    });

    it('Login Test', () => {
        cy.visit('http://127.0.0.1:8000/registration/login/');
        cy.fixture('user').then(user => {
            cy.get('#id_username').type(user.username);
            cy.get('#id_password').type(user.password);
        });
        cy.get('.registration_button').click();
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/user_app/home/'
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
