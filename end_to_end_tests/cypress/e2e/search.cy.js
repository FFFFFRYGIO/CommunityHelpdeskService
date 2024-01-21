describe('template spec', () => {

    beforeEach(() => {
        cy.fixture('user').then(user => {
            cy.register_user(user.username, user.password);
            cy.login_user(user.username, user.password);
        });
    });

    it('Search Test', () => {
        cy.visit('http://127.0.0.1:8000/user_app/search/');
        cy.location().should((loc) => {
            expect(loc.href).to.eq(
                'http://127.0.0.1:8000/user_app/search/'
            );
        });

        cy.get('#id_search_title').type('jak');
        cy.get('button[name="search_by_title"]').click();
        cy.get('.card-body').should('have.length', 10);

        cy.get('#id_search_phrase').type('ccleaner');
        cy.get('button[name="search_by_phrase"]').click();
        cy.get('.card-body').should('have.length', 1);

        cy.get('button').contains('Search by Ownership').click();
        cy.get('.card-body').should('have.length', 0);

    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.fixture('user').then(user => {
            cy.cleanup_user(user.username);
        });
    });

});
